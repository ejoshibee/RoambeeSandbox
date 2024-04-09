import { type Transform, JSXAttribute } from 'jscodeshift'
import * as path from 'path'

const transform: Transform = (fileInfo, api) => {
  const j = api.jscodeshift
  const root = j(fileInfo.source)
  // console.log(`root from transformation: ${JSON.stringify(root)}`)

  const fileContainsRouter = false

  if (fileContainsRouter) {
    return root.toSource()
  } else {
    return null
  }
}

export default transform
