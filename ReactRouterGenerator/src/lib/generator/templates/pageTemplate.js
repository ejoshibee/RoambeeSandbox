const pageTemplate = (name) => {
  return `
import React from 'react';

const ${name} = () => {
  return (
    <div>
      <h1>${name} Page</h1>
    </div>
  );
};

export default ${name};
  `.trim();
};

module.exports = { pageTemplate };
