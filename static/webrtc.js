class WebRTCConnection {
    constructor() {
        this.localStream = null;
        this.peerConnection = null;
        // Get server URL dynamically
        const SERVER_URL = window.location.origin;
        this.socket = io(SERVER_URL, {
            transports: ['websocket'],
            reconnection: true
        });
        this.roomId = null;
        this.setupSocketListeners();
    }

    async initialize() {
        try {
            // Get local stream
            this.localStream = await navigator.mediaDevices.getUserMedia({
                video: { 
                    width: { ideal: 640 },
                    height: { ideal: 480 }
                },
                audio: true
            });

            // Display local stream
            const localVideo = document.getElementById('localVideo');
            if (localVideo) {
                localVideo.srcObject = this.localStream;
            }

            return true;
        } catch (error) {
            console.error('Error accessing media devices:', error);
            return false;
        }
    }

    setupSocketListeners() {
        this.socket.on('connect', () => {
            console.log('Connected to signaling server');
        });

        this.socket.on('room_created', (roomId) => {
            console.log('Room created:', roomId);
            this.roomId = roomId;
            this.updateRoomInfo(roomId);
        });

        this.socket.on('room_joined', (roomId) => {
            console.log('Room joined:', roomId);
            this.roomId = roomId;
            this.updateRoomInfo(roomId);
            this.initiateCall();
        });

        this.socket.on('offer', async (offer) => {
            try {
                await this.handleOffer(offer);
            } catch (error) {
                console.error('Error handling offer:', error);
            }
        });

        this.socket.on('answer', async (answer) => {
            try {
                await this.handleAnswer(answer);
            } catch (error) {
                console.error('Error handling answer:', error);
            }
        });

        this.socket.on('ice_candidate', async (candidate) => {
            try {
                await this.handleIceCandidate(candidate);
            } catch (error) {
                console.error('Error handling ICE candidate:', error);
            }
        });

        this.socket.on('peer_disconnected', () => {
            console.log('Peer disconnected');
            this.handlePeerDisconnection();
        });
    }

    async createRoom() {
        if (!this.localStream) {
            console.error('Local stream not initialized');
            return;
        }
        this.socket.emit('create_room');
    }

    async joinRoom(roomId) {
        if (!this.localStream) {
            console.error('Local stream not initialized');
            return;
        }
        this.socket.emit('join_room', roomId);
    }

    async initiateCall() {
        try {
            this.peerConnection = new RTCPeerConnection({
                iceServers: [
                    { urls: 'stun:stun.l.google.com:19302' }
                ]
            });

            // Add local stream tracks to peer connection
            this.localStream.getTracks().forEach(track => {
                this.peerConnection.addTrack(track, this.localStream);
            });

            // Handle incoming stream
            this.peerConnection.ontrack = (event) => {
                const remoteVideo = document.getElementById('remoteVideo');
                if (remoteVideo && event.streams[0]) {
                    remoteVideo.srcObject = event.streams[0];
                }
            };

            // Handle ICE candidates
            this.peerConnection.onicecandidate = (event) => {
                if (event.candidate) {
                    this.socket.emit('ice_candidate', {
                        candidate: event.candidate,
                        roomId: this.roomId
                    });
                }
            };

            // Create and send offer
            const offer = await this.peerConnection.createOffer();
            await this.peerConnection.setLocalDescription(offer);
            this.socket.emit('offer', {
                offer: offer,
                roomId: this.roomId
            });

        } catch (error) {
            console.error('Error initiating call:', error);
        }
    }

    async handleOffer(offer) {
        try {
            if (!this.peerConnection) {
                this.peerConnection = new RTCPeerConnection({
                    iceServers: [
                        { urls: 'stun:stun.l.google.com:19302' }
                    ]
                });

                this.localStream.getTracks().forEach(track => {
                    this.peerConnection.addTrack(track, this.localStream);
                });

                this.peerConnection.ontrack = (event) => {
                    const remoteVideo = document.getElementById('remoteVideo');
                    if (remoteVideo && event.streams[0]) {
                        remoteVideo.srcObject = event.streams[0];
                    }
                };

                this.peerConnection.onicecandidate = (event) => {
                    if (event.candidate) {
                        this.socket.emit('ice_candidate', {
                            candidate: event.candidate,
                            roomId: this.roomId
                        });
                    }
                };
            }

            await this.peerConnection.setRemoteDescription(offer);
            const answer = await this.peerConnection.createAnswer();
            await this.peerConnection.setLocalDescription(answer);
            
            this.socket.emit('answer', {
                answer: answer,
                roomId: this.roomId
            });

        } catch (error) {
            console.error('Error handling offer:', error);
        }
    }

    async handleAnswer(answer) {
        try {
            if (this.peerConnection) {
                await this.peerConnection.setRemoteDescription(answer);
            }
        } catch (error) {
            console.error('Error handling answer:', error);
        }
    }

    async handleIceCandidate(candidate) {
        try {
            if (this.peerConnection) {
                await this.peerConnection.addIceCandidate(candidate);
            }
        } catch (error) {
            console.error('Error handling ICE candidate:', error);
        }
    }

    handlePeerDisconnection() {
        const remoteVideo = document.getElementById('remoteVideo');
        if (remoteVideo) {
            remoteVideo.srcObject = null;
        }
        
        if (this.peerConnection) {
            this.peerConnection.close();
            this.peerConnection = null;
        }
    }

    updateRoomInfo(roomId) {
        const roomInfo = document.getElementById('roomInfo');
        if (roomInfo) {
            roomInfo.textContent = `Room ID: ${roomId}`;
        }
    }

    disconnect() {
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
        }
        
        if (this.peerConnection) {
            this.peerConnection.close();
        }
        
        if (this.socket) {
            this.socket.disconnect();
        }
    }
}

// Initialize WebRTC on page load
document.addEventListener('DOMContentLoaded', () => {
    const webrtc = new WebRTCConnection();
    
    // Handle create room button
    const createRoomBtn = document.getElementById('createRoom');
    if (createRoomBtn) {
        createRoomBtn.addEventListener('click', async () => {
            await webrtc.initialize();
            webrtc.createRoom();
        });
    }
    
    // Handle join room button
    const joinRoomBtn = document.getElementById('joinRoom');
    const roomInput = document.getElementById('roomInput');
    if (joinRoomBtn && roomInput) {
        joinRoomBtn.addEventListener('click', async () => {
            const roomId = roomInput.value.trim();
            if (roomId) {
                await webrtc.initialize();
                webrtc.joinRoom(roomId);
            }
        });
    }
});
