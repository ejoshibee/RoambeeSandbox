import { promptRouteGeneration } from '../lib/generator/index.ts'

export const generate = async (): Promise<void> => {
  await promptRouteGeneration()
}
