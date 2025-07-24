const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const detectRole = require('../utils/detectRole');

exports.register = async (req, res) => {
  try {
    const { email, password } = req.body;
    const role = detectRole(email);
    const hashedPassword = await bcrypt.hash(password, 10);
    const newUser = await User.create({ email, password: hashedPassword, role });

    res.status(201).json({ message: 'User created', role });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};
