export interface VisionProvider {
  extractText(buffer: Buffer, mimeType: string, signal?: AbortSignal): Promise<string>;
}
