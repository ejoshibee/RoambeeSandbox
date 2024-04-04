import { generatePage } from '../lib/generator'

export const generate = (name) => {
  console.log(`Generating new page: ${name}`);
  generatePage(name);
};


