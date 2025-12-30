declare module 'react-plotly.js' {
    import * as Plotly from 'plotly.js';
    import * as React from 'react';

    interface PlotParams {
        data: Plotly.Data[];
        layout?: Partial<Plotly.Layout>;
        config?: Partial<Plotly.Config>;
        style?: React.CSSProperties;
        className?: string;
        useResizeHandler?: boolean;
        onInitialized?: (figure: Plotly.Figure, graphDiv: HTMLElement) => void;
        onUpdate?: (figure: Plotly.Figure, graphDiv: HTMLElement) => void;
        onPurge?: (figure: Plotly.Figure, graphDiv: HTMLElement) => void;
        onError?: (err: Error) => void;
    }

    const Plot: React.ComponentType<PlotParams>;
    export default Plot;
}
