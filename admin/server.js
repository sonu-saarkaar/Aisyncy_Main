const express = require('express');
const session = require('express-session');
const app = express();

// Admin credentials
const ADMIN_CREDENTIALS = [
    { username: 'admin1', password: 'securepass123' },
    { username: 'admin2', password: 'adminpass456' }
];

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('admin'));
app.use(session({
    secret: 'your-secret-key',
    resave: false,
    saveUninitialized: true
}));

// Authentication middleware
const requireAuth = (req, res, next) => {
    if (req.session.authenticated) {
        next();
    } else {
        res.redirect('/login.html');
    }
};

app.post('/admin/auth', (req, res) => {
    const { username, password } = req.body;
    const isValid = ADMIN_CREDENTIALS.some(
        admin => admin.username === username && admin.password === password
    );

    if (isValid) {
        req.session.authenticated = true;
        res.redirect('/dashboard.html');
    } else {
        res.redirect('/login.html');
    }
});

app.get('/admin/messages', requireAuth, (req, res) => {
    // Here you would fetch messages from your database
    // This is a placeholder example
    const messages = [
        { id: 1, sender: 'User1', message: 'Hello', status: 'unread' },
        { id: 2, sender: 'User2', message: 'Help needed', status: 'read' }
    ];
    res.json(messages);
});

app.post('/admin/reply', requireAuth, (req, res) => {
    const { messageId, reply } = req.body;
    // Here you would save the reply to your database
    res.json({ success: true });
});

app.listen(3000, () => {
    console.log('Admin panel running on port 3000');
});
