export const pageTemplate = (name: string) => {
  const capitalizedName = name.charAt(0).toUpperCase() + name.slice(1);

  return `
        import React from 'react';

        const ${capitalizedName} = () => {
          return (
            <div>
              <h1>${capitalizedName} Page</h1>
            </div>
          );
        };

        export default ${capitalizedName};
  `.trim();
};
