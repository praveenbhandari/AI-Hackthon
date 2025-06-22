declare module 'letta' {
  export interface ToolOptions {
    name: string;
    description: string;
    inputSchema: Record<string, string>;
    execute: (params: any) => Promise<any>;
  }

  export function Tool(options: ToolOptions): any;
  
  export interface AgentOptions {
    name: string;
    description: string;
    instructions?: string;
    tools?: any[];
    model?: string;
  }
  
  export function Agent(options: AgentOptions): any;
}
