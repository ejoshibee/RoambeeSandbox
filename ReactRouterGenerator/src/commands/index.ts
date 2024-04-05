/**
 * This file exposes any commands added to the cli tool. Currently only exposing generate, from generate.js, which generates pages
 */

// const generate = require('./generate');
// const init = require('./introduction');

import { generate } from './generate.ts'
import { init } from './introduction.ts'

export {
  generate,
  init
}
// module.exports = {
//   generate,
//   init,
// };
