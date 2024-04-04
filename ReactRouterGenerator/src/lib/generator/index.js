import fs from 'fs-extra'
import path from 'path'
import { pageTemplate } from './templates/pageTemplate'

/**
 * function to generate a page template. 
 * @param {string} name The name of the service/page for the application.
 * @param {string} type The type of page to be generated (TODO: create these types)
 */
const generatePage = async (name, type = null) => {
  const dirPath = path.join(process.cwd(), 'src/pages', name);
  const filePath = path.join(dirPath, `${name}.jsx`);
  try {
    await fs.ensureDir(dirPath);
    await fs.writeFile(filePath, pageTemplate(name));
    console.log(`Page ${name} generated successfully.`);
  } catch (error) {
    console.error(`Error generating page ${name}:`, error);
  }
};

module.exports = {
  generatePage,
};
