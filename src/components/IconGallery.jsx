import { DiceIcon, HeartIcon, RerollIcon } from "./Icons";
import styles from "./IconGallery.module.css";

const IconGallery = () => {
  const icons = [
    {
      name: "DiceIcon",
      component: DiceIcon,
      variants: [
        { size: 24, color: "white", fill: "black", label: "Small (24px)" },
        { size: 48, color: "white", fill: "black", label: "Medium (48px)" },
        { size: 72, color: "white", fill: "black", label: "Large (72px)" },
        { size: 48, color: "gold", fill: "darkblue", label: "Custom colors" },
      ],
    },
    {
      name: "HeartIcon",
      component: HeartIcon,
      variants: [
        { size: 24, color: "red", label: "Small (24px)" },
        { size: 48, color: "red", label: "Medium (48px)" },
        { size: 72, color: "red", label: "Large (72px)" },
        { size: 48, color: "pink", label: "Pink" },
        { size: 48, color: "crimson", label: "Crimson" },
      ],
    },
    {
      name: "RerollIcon",
      component: RerollIcon,
      variants: [
        { size: 24, color: "blue", fill: "lightblue", label: "Small (24px)" },
        { size: 48, color: "blue", fill: "lightblue", label: "Medium (48px)" },
        { size: 72, color: "blue", fill: "lightblue", label: "Large (72px)" },
        { size: 48, color: "green", fill: "lightgreen", label: "Green variant" },
      ],
    },
  ];

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Icon Gallery</h1>
      <p className={styles.description}>Development page for visualizing all available icons and their variants</p>

      <div className={styles.gallery}>
        {icons.map((icon) => (
          <div key={icon.name} className={styles.iconSection}>
            <h2 className={styles.iconName}>{icon.name}</h2>
            <div className={styles.variants}>
              {icon.variants.map((variant, index) => (
                <div key={index} className={styles.variantCard}>
                  <div className={styles.iconDisplay}>
                    <icon.component {...variant} />
                  </div>
                  <div className={styles.variantLabel}>{variant.label}</div>
                  <div className={styles.variantProps}>
                    <code>
                      size: {variant.size}
                      {variant.color && `, color: "${variant.color}"`}
                      {variant.fill && `, fill: "${variant.fill}"`}
                    </code>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default IconGallery;
