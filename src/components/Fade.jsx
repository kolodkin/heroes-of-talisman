import React, { createContext, forwardRef, useContext } from "react";

import styles from "./Fade.module.css";

const DELAY_STEP = 0.07;

const FadeContext = createContext(false);

export const FadeProvider = FadeContext.Provider;

const Fade = forwardRef(({ children, className, ...rest }, ref) => {
  const leaving = useContext(FadeContext);

  return (
    <div ref={ref} className={className} {...rest}>
      {React.Children.map(children, (child, index) =>
        child ? (
          <div
            className={leaving ? styles.itemLeaving : styles.item}
            style={{ "--enter-delay": `${index * DELAY_STEP}s` }}
          >
            {child}
          </div>
        ) : null,
      )}
    </div>
  );
});

Fade.displayName = "Fade";

export default Fade;
