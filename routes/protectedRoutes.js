const express = require('express');
const auth = require('../middleware/authMiddleware');
const roleCheck = require('../middleware/roleCheck');

const router = express.Router();

router.post('/post-text', auth, (req, res) => {
  res.send('Text posted successfully!');
});

router.post('/post-media', auth, roleCheck, (req, res) => {
  res.send('Photo/Video/Story posted successfully!');
});

module.exports = router;
