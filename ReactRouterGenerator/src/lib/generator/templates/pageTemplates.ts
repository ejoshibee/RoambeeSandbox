export type TemplateType = 'withLoader' | 'deferredLoader' | 'withParams' | 'authenticatedRoute' | 'lazyLoaded' | 'notFound' | 'layout'

export const pageTemplate = (name: string, type: TemplateType | null = null): string => {
  const capitalizedName = name[0].toUpperCase() + name.slice(1)

  switch (type) {
    case 'withLoader':
      return `
        import React from 'react';
        import { useLoaderData } from 'react-router-dom';

        export const loader = async () => {
          // api call to return an object {message: 'Hello from the loader!'}
          const data = await fakeApiCall()
          return data
        }

        const ${capitalizedName} = () => {
          
          const data = useLoaderData()
          
          return (
            <div>
              <h1>${capitalizedName} Page</h1>
              <p>{data.message}</p>
            </div>
          );
        };

        export default ${capitalizedName};
  `.trim()
    case 'deferredLoader':
      return `
      import React, { Suspense } from 'react';
      import { useLoaderData, Await, defer } from 'react-router-dom';

      export const loader = async () => {
        // expensive api call to return a list of objects {message: [SOME ARRAY]}
        const dataPromise = fakeApiCall()
        return defer({data: dataPromise})
      }

      const ${capitalizedName} = () => {
        
        const loaderData = useLoaderData()
        
        return (
          <div>
            <h1>${capitalizedName} Page</h1>
            <Suspense fallback={<div>Loading...</div>}>
              <Await resolve={loaderData.data} error={<h1>Error!</h1>}>
                {
                  (data) => {
                    return data.map((ele) => {
                      // return your component here to render your element and its props
                    })
                  }
                }
              </Await>
            </Suspense>
          </div>
        );
      };

      export default ${capitalizedName};
  `.trim()
    case 'withParams':
      return `
      import React from 'react';
      import { useParams } from 'react-router-dom';
      
      const ${capitalizedName} = () => {
        // Use 'useParams' hook to access the route parameters
        const params = useParams();
      
        // Access a specific parameter, assuming the route parameter name is 'id'
        const { id } = params;
      
        return (
          <div>
            <h1> ${capitalizedName} Page</h1>
            <p>This is a sample page</p>
            <p>Route parameter (id): {id}</p>
          </d
        );
      };
      
      export default ${capitalizedName};
  `.trim()

    // AuthenticatedRoute Template
    case 'authenticatedRoute':
      return `
    import React from 'react';
    import { Navigate } from 'react-router-dom';

    const ${capitalizedName} = ({ children }) => {
      const isAuthenticated = checkAuth(); // Implement your authentication logic here

      if (!isAuthenticated) {
        // Redirect them to the /login page, but save the current location they were trying to go to
        return <Navigate to="/login" replace />;
      }

      return children;
    };

    export default ${capitalizedName};
  `.trim()

      // LazyLoadedRoute Template
    case 'lazyLoaded':
      return `
    import React, { Suspense, lazy } from 'react';

    const ${capitalizedName}Component = lazy(() => import('./path/to/${capitalizedName}Component'));

    const ${capitalizedName} = () => (
      <Suspense fallback={<div>Loading...</div>}>
        <${capitalizedName}Component />
      </Suspense>
    );

    export default ${capitalizedName};
  `.trim()

      // NotFoundPage Template
    case 'notFound':
      return `
    import React from 'react';

    const ${capitalizedName} = () => (
      <div>
        <h1>404 Not Found</h1>
        <p>The page you are looking for does not exist.</p>
      </div>
    );

    export default ${capitalizedName};
  `.trim()

      // LayoutComponent Template
    case 'layout':
      return `
    import React from 'react';

    const ${capitalizedName} = ({ children }) => (
      <div>
        <header>Header Content</header>
        <main>{children}</main>
        <footer>Footer Content</footer>
      </div>
    );

    export default ${capitalizedName};
  `.trim()
    default:
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
    `.trim()
  }
}
