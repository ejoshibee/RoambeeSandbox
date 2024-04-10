import { type Transform } from 'jscodeshift'

const transform: Transform = (fileInfo, api) => {
  const j = api.jscodeshift
  const root = j(fileInfo.source)

  // find all 'Route' nodes in the tree
  const routes = root.find(j.JSXElement, {
    openingElement: {
      name: {
        name: 'Route'
      }
    }
  })

  // check that routes were found
  if (routes.size() > 0) {
    // Extract the first <Route /> component
    console.log('Found <Route /> components')

    routes.forEach((path, i) => {
      // Serialize the <Route /> to a string including formatting
      const routeStr = j(path).toSource({ quote: 'single', trailingComma: true })
      console.log(`Route ${i + 1}: ${routeStr}`)
    })

    // const firstRoute = routes.at(0).nodes()[0]

    // Serialize the first <Route /> to a string including formatting
    // const firstRouteStr = j(firstRoute).toSource({ quote: 'single', trailingComma: true })
  } else {
    console.log('No <Route /> components found.')
  }

  const fileContainsRouter = false

  if (fileContainsRouter) {
    return root.toSource()
  } else {
    return null
  }
}

export default transform
