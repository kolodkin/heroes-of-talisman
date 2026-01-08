import React from "react";
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
  return (
    <div className={styles.container}>
      {/* Left side: Fixed action button */}
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

      {/* Right side: Title and scrollable content */}
      <div className={styles.rightSide}>
        {/* Title section */}
        {title && <div className={styles.title}>{title}</div>}

        {/* Scrollable content section */}
        <div className={styles.content} data-shared-content>
          {content}
        </div>
      </div>
    </div>
  );
};
