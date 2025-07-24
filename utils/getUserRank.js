// Use axios/fetch to call their service
const axios = require('axios');

module.exports = async function getUserRank(userId) {
  const response = await axios.get(`http://rankings-api.com/rank/${userId}`);
  return response.data.rank;
};
