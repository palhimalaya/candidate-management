import { useState, useEffect, useRef } from 'react';

export function useDebounce<T>(value: T, delay: number = 500): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);
  const delayRef = useRef(delay);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delayRef.current);

    return () => clearTimeout(handler);
  }, [value]);

  return debouncedValue;
}