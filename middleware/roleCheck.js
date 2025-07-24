const getUserRank = require('../utils/getUserRank');

module.exports = async function (req, res, next) {
  const { role, id } = req.user;

  // Staff always allowed
  if (role === 'staff') return next();

  // If student, check rank
  try {
    const rank = await getUserRank(id); // fetch rank by userId
    if (rank && rank <= 50) {
      return next();
    } else {
      return res.status(403).json({ message: "You must be in top 50 to post media." });
    }
  } catch (err) {
    return res.status(500).json({ message: "Error checking rank." });
  }
};
