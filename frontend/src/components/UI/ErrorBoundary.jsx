import { Component } from 'react';
import PropTypes from 'prop-types';

export class ErrorBoundary extends Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error('UI ErrorBoundary caught:', error, errorInfo);
    }

    handleRetry = () => {
        this.setState({ hasError: false, error: null });
    };

    render() {
        if (this.state.hasError) {
            return (
                <div className="glass-card" style={{ margin: '2rem', padding: '1.25rem' }}>
                    <h2>Something went wrong</h2>
                    <p>
                        We hit an unexpected UI error. You can retry, or refresh the page.
                    </p>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button className="btn btn-secondary" onClick={this.handleRetry}>Retry</button>
                        <button className="btn btn-secondary" onClick={() => window.location.reload()}>Refresh</button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

ErrorBoundary.propTypes = {
    children: PropTypes.node,
};

export default ErrorBoundary;
