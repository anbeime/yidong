// 模拟React类型声明
declare module 'react' {
  export interface Component<P = {}, S = {}> {
    props: P;
    state: S;
    setState(state: Partial<S>): void;
    render(): React.ReactNode;
  }
  
  export class Component<P = {}, S = {}> {
    constructor(props: P);
    props: P;
    state: S;
    setState(state: Partial<S>): void;
    render(): React.ReactNode;
  }

  export interface ErrorInfo {
    componentStack?: string;
  }

  export type ReactNode = string | number | boolean | null | undefined | React.ReactElement | ReactNode[];
  export type ReactElement = any;
  export type FC<P = {}> = (props: P) => ReactElement;
  
  export function useState<T>(initialState: T): [T, (newState: T) => void];
  export function useEffect(effect: () => void | (() => void), deps?: any[]): void;
  export function createElement(type: any, props?: any, ...children: any[]): ReactElement;
  
  const React: {
    Component: typeof Component;
    createElement: typeof createElement;
    useState: typeof useState;
    useEffect: typeof useEffect;
  };
  
  export default React;
}

declare module 'react-dom' {
  export const createRoot: (container: Element) => {
    render: (element: any) => void;
  };
}

declare module 'react-router-dom' {
  export function useNavigate(): (path: string) => void;
  export function useLocation(): { pathname: string };
  export const Routes: any;
  export const Route: any;
  export const BrowserRouter: any;
}

declare module 'antd' {
  export const Layout: any;
  export const Menu: any;
  export const theme: any;
  export const Avatar: any;
  export const Dropdown: any;
  export const Space: any;
  export const Typography: any;
  export const Badge: any;
  export const notification: any;
  export const ConfigProvider: any;
  export const Card: any;
  export const Row: any;
  export const Col: any;
  export const Statistic: any;
  export const Progress: any;
  export const Table: any;
  export const Tag: any;
  export const Button: any;
  export const Alert: any;
}

declare module 'antd/locale/zh_CN' {
  const zhCN: any;
  export default zhCN;
}

declare module '@ant-design/icons' {
  export const DashboardOutlined: any;
  export const CloudOutlined: any;
  export const BarChartOutlined: any;
  export const SettingOutlined: any;
  export const BellOutlined: any;
  export const UserOutlined: any;
  export const MenuFoldOutlined: any;
  export const MenuUnfoldOutlined: any;
  export const ThunderboltOutlined: any;
  export const DollarOutlined: any;
  export const WarningOutlined: any;
  export const ArrowUpOutlined: any;
  export const ArrowDownOutlined: any;
}

declare module 'echarts-for-react' {
  const ReactECharts: any;
  export default ReactECharts;
}

declare module 'dayjs' {
  const dayjs: any;
  export default dayjs;
}