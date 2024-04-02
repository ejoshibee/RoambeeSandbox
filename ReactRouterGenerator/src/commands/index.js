/**
 * This file exposes any commands added to the cli tool. Currently only exposing generate, from generate.js, which generates pages
 */

const generate = require('./generate');

module.exports = {
  generate,
};
