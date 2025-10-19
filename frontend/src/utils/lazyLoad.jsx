import { lazy, Suspense } from 'react';
import { Loader2 } from 'lucide-react';

/**
 * Lazy loading utility for React components
 * Provides a loading fallback while components are being loaded
 */

const LoadingFallback = () => (
  <div className="flex items-center justify-center w-full h-screen bg-gradient-to-br from-slate-50 to-slate-100">
    <div className="flex flex-col items-center gap-4">
      <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
      <p className="text-slate-600 font-medium">Loading...</p>
    </div>
  </div>
);

/**
 * Higher-order component for lazy loading pages
 * @param {Function} importFunc - Dynamic import function
 * @returns {React.Component} - Wrapped component with Suspense
 */
export const lazyLoad = (importFunc) => {
  const LazyComponent = lazy(importFunc);
  return (props) => (
    <Suspense fallback={<LoadingFallback />}>
      <LazyComponent {...props} />
    </Suspense>
  );
};

/**
 * Optimize image loading with lazy loading and responsive sizes
 * @param {string} src - Image source URL
 * @param {string} alt - Alt text for accessibility
 * @param {object} options - Additional options (width, height, className)
 * @returns {React.Component} - Optimized image component
 */
export const OptimizedImage = ({ src, alt, width = 'auto', height = 'auto', className = '', ...props }) => {
  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      width={width}
      height={height}
      className={`${className} transition-opacity duration-300`}
      {...props}
    />
  );
};

/**
 * Debounce utility for optimizing event handlers
 * @param {Function} func - Function to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {Function} - Debounced function
 */
export const debounce = (func, delay = 300) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

/**
 * Throttle utility for optimizing scroll and resize handlers
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} - Throttled function
 */
export const throttle = (func, limit = 300) => {
  let inThrottle;
  return (...args) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

export default {
  lazyLoad,
  OptimizedImage,
  debounce,
  throttle,
};

