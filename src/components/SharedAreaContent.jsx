import React, { useEffect, useCallback } from "react";

import styles from "./SharedAreaContent.module.css";

/**
 * SharedAreaContent component for consolidating all game stage views
 *
 * @param {Object} props
 * @param {React.ReactNode} props.title - Title content/HTML to display
 * @param {React.ReactNode} props.content - Main content/HTML to display (scrollable)
 * @param {Function} props.onActionClick - Click handler for the action button
 * @param {string|React.ReactNode} props.actionButtonContent - Text or JSX to display on the action button
 * @param {boolean} props.actionButtonDisabled - Whether the action button is disabled
 * @param {Object} props.actionButtonDataAttrs - Custom data attributes for the action button
 */
export const SharedAreaContent = ({
  title,
  content,
  onActionClick,
  actionButtonContent,
  actionButtonDisabled = false,
  actionButtonDataAttrs = {},
}) => {
  const handleKeyDown = useCallback(
    (e) => {
      if (e.key !== "Enter") return;
      if (actionButtonDisabled || !onActionClick || !actionButtonContent) return;

      const isDesktop = window.matchMedia("(min-width: 1024px)").matches;
      if (!isDesktop) return;

      e.preventDefault();
      onActionClick();
    },
    [onActionClick, actionButtonDisabled, actionButtonContent],
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  return (
    <div className={styles.container}>
      {/* Action button (positioned at end: right in LTR, left in RTL) */}
      <div className={styles.actionButtonContainer}>
        {onActionClick && actionButtonContent && (
          <button
            className={styles.actionButton}
            onClick={onActionClick}
            disabled={actionButtonDisabled}
            data-action-button
            {...actionButtonDataAttrs}
          >
            {actionButtonContent}
          </button>
        )}
      </div>

      {/* Content area: Title and scrollable content (positioned at start) */}
      <div className={styles.rightSide}>
        {title && <div className={styles.title}>{title}</div>}
        <div className={styles.content} data-shared-content>
          {content}
        </div>
      </div>
    </div>
  );
};
