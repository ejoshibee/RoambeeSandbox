const fs = require('fs-extra');
const path = require('path');
const { pageTemplate } = require('./templates/pageTemplate');

const generatePage = async (name) => {
  const dirPath = path.join(process.cwd(), 'src/pages', name);
  const filePath = path.join(dirPath, `${name}.jsx`);
  try {
    await fs.ensureDir(dirPath);
    await fs.writeFile(filePath, pageTemplate(name));
    console.log('test console.log')
    console.log(`Page ${name} generated successfully.`);
  } catch (error) {
    console.error(`Error generating page ${name}:`, error);
  }
};

module.exports = {
  generatePage,
};
