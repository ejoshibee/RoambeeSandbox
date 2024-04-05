import { generatePage } from '../lib/generator/index.ts'
import { logger } from '../lib/logger.ts'

export const generate = async (name: string): Promise<void> => {
  logger.info(`Generating new page: ${name}`)
  await generatePage(name)
}
