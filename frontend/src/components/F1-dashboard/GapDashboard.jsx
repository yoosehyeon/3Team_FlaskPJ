import { motion, useMotionValue, useTransform, animate } from 'framer-motion';
import { useEffect } from 'react';

const CountUpNumber = ({ from = 0, to = 0, duration = 3 }) => {
  const count = useMotionValue(from);
  const rounded = useTransform(count, (latest) => Math.round(latest));

  useEffect(() => {
    const controls = animate(count, to, { duration });
    return () => controls.stop();
  }, [count, to, duration]);

  return <motion.span className="text-6xl font-bold">{rounded}</motion.span>;
};
