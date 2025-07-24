module.exports = function detectRole(email) {
  if (/^su-\d{5}@sitare\.org$/.test(email)) return 'student';
  if (/^[a-z]+\@sitare\.org$/.test(email)) return 'staff';
  throw new Error('Invalid email format');
}
