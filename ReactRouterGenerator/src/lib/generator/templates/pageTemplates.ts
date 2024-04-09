export type TemplateType = 'withLoader' | 'deferredLoader' | 'withParams' | 'authenticatedRoute' | 'lazyLoaded' | 'notFound' | 'layout'
/**
 * A function to generate page templates for react router based on input type, encapsulating input name and api path
 *
 * NOTE: addition or deletion of a template in the switch statement must be reflected by addition or deleted of a type in the TemplateType above AND
 * addition or deletion of template option in the the /generator/index.ts inquirer prompt
 * @param name the name of the component to be generated (The first letter is auto-capitalized per component name standards)
 * @param type the type of the component to be generated (with a deferrer-loader, with URL params, etc...)
 * @param apiPath the api path to be used in the component
 * @returns a string of the page template to be written to the file in the generatePage function invocation
 *
 * @example
 * ```tsx
 * generatePage('home', 'withLoader', '/api/home')
 * ```
 */
export const pageTemplate = (name: string, type: TemplateType, apiPath: string): string => {
  const capitalizedName = name[0].toUpperCase() + name.slice(1)

  switch (type) {
    // with
    case 'withLoader':
      return (
`
import React from 'react'
import { useLoaderData } from 'react-router-dom'

export const loader = async () => {
  // api call to return an object {message: 'Hello from the loader!'}
  const data = await fetch('/api/${apiPath}')
  return data
}

const ${capitalizedName} = () => {
          
  const data = useLoaderData()
          
  return (
    <div>
      <h1>${capitalizedName} Page</h1>
      <p>{data.message}</p>
    </div>
  )
}

export default ${capitalizedName}
  `).trim()

      // with deferred loader template
    case 'deferredLoader':
      return `
import React, { Suspense } from 'react'
import { useLoaderData, Await, defer } from 'react-router-dom'

export const loader = async () => {
  // expensive api call to return a list of objects {message: [SOME ARRAY]}
  const dataPromise = fetch('/api/${apiPath}')
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
  )
}

export default ${capitalizedName}
  `.trim()

      // with URL params
    case 'withParams':
      return `
import React from 'react'
import { useParams } from 'react-router-dom'

const ${capitalizedName} = () => {
  // Use 'useParams' hook to access the route parameters
  const params = useParams()

  // Access a specific parameter, assuming the route parameter name is 'id'
  const { id } = params

  return (
    <div>
      <h1> ${capitalizedName} Page</h1>
      <p>This is a sample page</p>
      <p>Route parameter (id): {id}</p>
    </d
  )
}

export default ${capitalizedName}
  `.trim()

    // AuthenticatedRoute Template
    case 'authenticatedRoute':
      return `
import React from 'react'
import { Navigate } from 'react-router-dom'

const ${capitalizedName} = ({ children }) => {
  const isAuthenticated = checkAuth() // Implement your authentication logic here

  if (!isAuthenticated) {
    // Redirect them to the /login page, but save the current location they were trying to go to
    return <Navigate to="/login" replace />
  }

  return children
}

export default ${capitalizedName}
  `.trim()

      // LazyLoadedRoute Template
    case 'lazyLoaded':
      return `
import React, { Suspense, lazy } from 'react'

const ${capitalizedName}Component = lazy(() => import('./path/to/${capitalizedName}Component'))

const ${capitalizedName} = () => (
  <Suspense fallback={<div>Loading...</div>}>
    <${capitalizedName}Component />
  </Suspense>
)

export default ${capitalizedName}
  `.trim()

      // NotFoundPage Template
    case 'notFound':
      return `
import React from 'react'

const ${capitalizedName} = () => (
  <div>
    <h1>404 Not Found</h1>
    <p>The page you are looking for does not exist.</p>
  </div>
)

export default ${capitalizedName}
  `.trim()

      // LayoutComponent Template
    case 'layout':
      return `
import React from 'react'

const ${capitalizedName} = ({ children }) => (
  <div>
    <header>Header Content</header>
    <main>{children}</main>
    <footer>Footer Content</footer>
  </div>
)

export default ${capitalizedName}
  `.trim()

      // default/erronous input case component
    default:
      return `
  import React from 'react'

  const ${capitalizedName} = () => {
    return (
      <div>
        <h1>${capitalizedName} Page</h1>
      </div>
    )
  }

  export default ${capitalizedName}
    `.trim()
  }
}
