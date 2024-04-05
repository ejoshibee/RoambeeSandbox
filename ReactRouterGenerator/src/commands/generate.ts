import { generatePage } from '../lib/generator/index.ts'

export const generate = (name: string) => {
  console.log(`Generating new page: ${name}`);
  generatePage(name);
};


