import { useEffect, useRef, useState } from "react";

/**
 * Hook to detect if a container has horizontal scroll and apply appropriate alignment
 * Returns a ref to attach to the scrollable container and alignment class
 */
export const useScrollAlignment = () => {
  const containerRef = useRef(null);
  const [hasScroll, setHasScroll] = useState(false);

  useEffect(() => {
    const checkScroll = () => {
      if (containerRef.current) {
        const needsScroll = containerRef.current.scrollWidth > containerRef.current.clientWidth;
        setHasScroll(needsScroll);
      }
    };

    // Check on mount and when window resizes
    checkScroll();
    window.addEventListener("resize", checkScroll);

    // Use ResizeObserver for more accurate detection
    let resizeObserver;
    if (containerRef.current && typeof ResizeObserver !== "undefined") {
      resizeObserver = new ResizeObserver(checkScroll);
      resizeObserver.observe(containerRef.current);
    }

    return () => {
      window.removeEventListener("resize", checkScroll);
      if (resizeObserver) {
        resizeObserver.disconnect();
      }
    };
  }, []);

  return { containerRef, hasScroll };
};
