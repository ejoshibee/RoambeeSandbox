import { promptIntroduction } from '../lib/introduction/index.ts'

export const init = async (): Promise<void> => {
  await promptIntroduction()
}
