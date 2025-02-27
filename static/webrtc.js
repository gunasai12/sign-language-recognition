class WebRTCHandler {
    constructor() {
        this.localStream = null;
        this.peerConnection = null;
        this.room = null;
        this.userType = 'deaf'; // Default to deaf user

        // Get server URL dynamically
        const SERVER_URL = window.location.origin;
        this.socket = io(SERVER_URL, {
            transports: ['websocket'],
            reconnection: true
        });

        // WebRTC configuration with STUN servers
        this.configuration = {
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' },
                { urls: 'stun:stun2.l.google.com:19302' },
                { urls: 'stun:stun3.l.google.com:19302' },
                { urls: 'stun:stun4.l.google.com:19302' }
            ]
        };

        this.setupSocketListeners();
        this.setupUIListeners();
    }

    setupUIListeners() {
        // User type selection
        document.querySelectorAll('input[name="userType"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.userType = e.target.value;
                this.updateUIForUserType();
            });
        });

        // Room controls
        document.getElementById('createRoom').addEventListener('click', () => this.createRoom());
        document.getElementById('joinRoom').addEventListener('click', () => {
            const roomId = document.getElementById('roomInput').value;
            if (roomId) this.joinRoom(roomId);
        });
    }

    updateUIForUserType() {
        const detectionControls = document.querySelector('.video-controls');
        const detectionBox = document.querySelector('.detection-box');

        if (this.userType === 'deaf') {
            detectionControls.style.display = 'flex';
            detectionBox.style.display = 'block';
        } else {
            detectionControls.style.display = 'none';
            detectionBox.style.display = 'none';
        }
    }

    async setupMediaStream() {
        try {
            this.localStream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: true
            });

            const localVideo = document.getElementById('localVideo');
            localVideo.srcObject = this.localStream;

            return true;
        } catch (error) {
            console.error('Error accessing media devices:', error);
            alert('Failed to access camera and microphone. Please ensure permissions are granted.');
            return false;
        }
    }

    async createRoom() {
        if (!this.localStream && !(await this.setupMediaStream())) return;

        const roomId = Math.random().toString(36).substring(7);
        this.socket.emit('create', { room: roomId });
        this.room = roomId;
        
        document.getElementById('roomInfo').textContent = `Room ID: ${roomId}`;
        document.getElementById('roomInput').value = roomId;
    }

    async joinRoom(roomId) {
        if (!this.localStream && !(await this.setupMediaStream())) return;

        this.socket.emit('join', { room: roomId });
        this.room = roomId;
        
        document.getElementById('roomInfo').textContent = `Room ID: ${roomId}`;
    }

    setupSocketListeners() {
        this.socket.on('room_created', async (data) => {
            console.log('Room created:', data.room);
            this.initializePeerConnection();
        });

        this.socket.on('room_joined', async (data) => {
            console.log('Room joined:', data.room);
            this.initializePeerConnection();
            this.createAndSendOffer();
        });

        this.socket.on('offer', async (data) => {
            if (!this.peerConnection) {
                this.initializePeerConnection();
            }
            await this.peerConnection.setRemoteDescription(new RTCSessionDescription(data.offer));
            const answer = await this.peerConnection.createAnswer();
            await this.peerConnection.setLocalDescription(answer);
            this.socket.emit('answer', { answer, room: this.room });
        });

        this.socket.on('answer', async (data) => {
            await this.peerConnection.setRemoteDescription(new RTCSessionDescription(data.answer));
        });

        this.socket.on('ice_candidate', async (data) => {
            if (data.candidate) {
                try {
                    await this.peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate));
                } catch (error) {
                    console.error('Error adding ice candidate:', error);
                }
            }
        });

        this.socket.on('detection_result', (data) => {
            if (this.userType === 'non-deaf') {
                this.updateDetectionResult(data);
            }
        });
    }

    initializePeerConnection() {
        this.peerConnection = new RTCPeerConnection(this.configuration);

        this.localStream.getTracks().forEach(track => {
            this.peerConnection.addTrack(track, this.localStream);
        });

        this.peerConnection.onicecandidate = (event) => {
            if (event.candidate) {
                this.socket.emit('ice_candidate', {
                    candidate: event.candidate,
                    room: this.room
                });
            }
        };

        this.peerConnection.ontrack = (event) => {
            const remoteVideo = document.getElementById('remoteVideo');
            if (remoteVideo.srcObject !== event.streams[0]) {
                remoteVideo.srcObject = event.streams[0];
            }
        };

        this.peerConnection.onconnectionstatechange = () => {
            if (this.peerConnection.connectionState === 'connected') {
                document.getElementById('connectionStatus').innerHTML = 
                    '<i class="fas fa-check-circle"></i> Connected';
                document.getElementById('connectionStatus').classList.add('connected');
            } else {
                document.getElementById('connectionStatus').innerHTML = 
                    '<i class="fas fa-times-circle"></i> Disconnected';
                document.getElementById('connectionStatus').classList.remove('connected');
            }
        };
    }

    async createAndSendOffer() {
        try {
            const offer = await this.peerConnection.createOffer();
            await this.peerConnection.setLocalDescription(offer);
            this.socket.emit('offer', { offer, room: this.room });
        } catch (error) {
            console.error('Error creating offer:', error);
        }
    }

    updateDetectionResult(data) {
        const resultElement = document.getElementById('detectionResult');
        const historyElement = document.getElementById('detectionHistory');
        
        // Update current result
        resultElement.innerHTML = `
            <div class="result-label">${data.label}</div>
            <div class="result-confidence">Confidence: ${(data.confidence * 100).toFixed(2)}%</div>
        `;
        resultElement.classList.add('active');

        // Add to history
        const time = new Date().toLocaleTimeString();
        const historyEntry = document.createElement('div');
        historyEntry.className = 'history-entry';
        historyEntry.innerHTML = `
            <span class="time">${time}</span>
            <span class="label">${data.label}</span>
            <span class="confidence">${(data.confidence * 100).toFixed(2)}%</span>
        `;
        
        historyElement.insertBefore(historyEntry, historyElement.firstChild);
        if (historyElement.children.length > 10) {
            historyElement.removeChild(historyElement.lastChild);
        }
    }
}

// Initialize WebRTC handler
const webRTC = new WebRTCHandler();
