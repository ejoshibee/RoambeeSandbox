const { generatePage } = require('../lib/generator');

const generate = (name) => {
  console.log(`Generating new page: ${name}`);
  generatePage(name);
};

module.exports = generate;
