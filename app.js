require('dotenv').config(); // To load your .env variables

const express = require('express');
const connectDB = require('./config/db'); // Import your DB connection

const app = express();

// Connect to MongoDB
connectDB();

// Middlewares
app.use(express.json());

// Your routes
app.use('/api/auth', require('./routes/authRoutes'));
app.use('/api/post', require('./routes/protectedRoutes'));

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`🚀 Server is running on port ${PORT}`);
});
