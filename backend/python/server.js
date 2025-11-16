const express = require('express');
const path = require('path');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Serve static files from public directory
app.use(express.static(path.join(__dirname, 'public')));

// In-memory storage for demo purposes (use a database in production)
let users = {};
let medicalRecords = {};

// API Routes

// Handle data submission (from the sendData function in frontend)
app.post('/api/data', (req, res) => {
    try {
        const { input } = req.body;
        
        if (!input || typeof input !== 'string') {
            return res.status(400).json({ error: 'Invalid input' });
        }
        
        let response;
        
        // Simple processing logic (can be enhanced with AI/ML)
        const lowerInput = input.toLowerCase().trim();
        
        if (lowerInput === 'hello' || lowerInput === 'hi') {
            response = 'Hello! How can I assist you with your healthcare needs today?';
        } else if (lowerInput.includes('appointment')) {
            response = 'I can help you schedule an appointment. What type of appointment do you need?';
        } else if (lowerInput.includes('symptom') || lowerInput.includes('pain')) {
            response = 'Please describe your symptoms in detail, and I\'ll help you find appropriate care or suggest when to seek medical attention.';
        } else if (lowerInput.includes('emergency')) {
            response = 'For emergencies, please call 911 immediately. For HealthCare Connect support, call 1-800-HEALTH.';
        } else if (lowerInput.includes('mental health') || lowerInput.includes('depression') || lowerInput.includes('anxiety')) {
            response = 'Mental health support is available. You can start an anonymous counseling session or call the Suicide & Crisis Lifeline at 988.';
        } else {
            response = `I received your message: "${input}". How can HealthCare Connect assist you today? You can ask about appointments, symptoms, or general health information.`;
        }
        
        res.json({ response });
    } catch (error) {
        console.error('Error processing data:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Login endpoint (server-side authentication)
app.post('/api/login', (req, res) => {
    const { email, password } = req.body;
    
    if (!email || !password) {
        return res.status(400).json({ success: false, message: 'Email and password are required' });
    }
    
    // Simple authentication (use proper auth in production)
    if (users[email] && users[email].password === password) {
        res.json({
            success: true,
            user: {
                name: users[email].name,
                email: email
            }
        });
    } else {
        res.status(401).json({ success: false, message: 'Invalid credentials' });
    }
});

// Signup endpoint (server-side registration)
app.post('/api/signup', (req, res) => {
    const { name, email, password, phone } = req.body;
    
    if (!name || !email || !password || !phone) {
        return res.status(400).json({ success: false, message: 'All fields are required' });
    }
    
    if (users[email]) {
        return res.status(400).json({ success: false, message: 'User already exists' });
    }
    
    users[email] = {
        name,
        password, // In production, hash passwords
        phone
    };
    
    res.json({
        success: true,
        user: {
            name,
            email
        }
    });
});

// Get medical records for a user
app.get('/api/medical-records/:email', (req, res) => {
    const { email } = req.params;
    
    if (!users[email]) {
        return res.status(404).json({ error: 'User not found' });
    }
    
    const records = medicalRecords[email] || [];
    res.json({ records });
});

// Add medical record for a user
app.post('/api/medical-records/:email', (req, res) => {
    const { email } = req.params;
    const { date, type, description, doctor } = req.body;
    
    if (!users[email]) {
        return res.status(404).json({ error: 'User not found' });
    }
    
    const record = {
        date: date || new Date().toISOString().split('T')[0],
        type: type || 'General',
        description: description || '',
        doctor: doctor || 'Unknown'
    };
    
    if (!medicalRecords[email]) {
        medicalRecords[email] = [];
    }
    medicalRecords[email].push(record);
    
    res.json({ success: true, record });
});

// Schedule appointment
app.post('/api/appointments', (req, res) => {
    const { type, date, time, doctor } = req.body;
    
    const appointment = {
        type: type || 'General',
        date: date || 'TBD',
        time: time || 'TBD',
        doctor: doctor || 'Assigned by system',
        status: 'Scheduled',
        id: Date.now() // Simple ID generation
    };
    
    // In a real app, save to database
    res.json({ success: true, appointment });
});

// Get emergency contacts
app.get('/api/emergency-contacts', (req, res) => {
    const contacts = [
        { name: 'Emergency Services', number: '911' },
        { name: 'Poison Control', number: '1-800-222-1222' },
        { name: 'Suicide Prevention Lifeline', number: '988' },
        { name: 'HealthCare Connect Support', number: '1-800-HEALTH' },
        { name: 'Mental Health Crisis', number: '1-800-950-NAMI' }
    ];
    res.json({ contacts });
});

// Mock SDK endpoints (since the frontend references them)
app.get('/_sdk/data_sdk.js', (req, res) => {
    res.type('application/javascript');
    res.send(`
        // Mock Data SDK
        window.dataSdk = {
            init: function(config) { console.log('Data SDK initialized', config); },
            track: function(event) { console.log('Event tracked:', event); }
        };
    `);
});

app.get('/_sdk/element_sdk.js', (req, res) => {
    res.type('application/javascript');
    res.send(`
        // Mock Element SDK
        window.elementSdk = {
            init: function(config) { 
                console.log('Element SDK initialized', config);
                // Call onConfigChange if provided
                if (config.onConfigChange) {
                    config.onConfigChange(config.defaultConfig);
                }
            }
        };
    `);
});

// Serve the main HTML file for all other routes
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something went wrong!' });
});

// Start server
app.listen(PORT, () => {
    console.log(`HealthCare Connect server running on http://localhost:${PORT}`);
});
