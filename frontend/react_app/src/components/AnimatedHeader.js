import React from "react";
import { motion } from "framer-motion";
import Lottie from "lottie-react";
import heroAnim from "../assets/hero.json";

export default function AnimatedHeader() {
    return (
        <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="flex flex-col items-center text-center mb-8"
        >
            <div className="w-48 mb-4">
                <Lottie animationData={heroAnim} loop />
            </div>
            <h1 className="text-3xl font-bold text-blue-700">
                Speech → Indian Sign Language Translator
            </h1>
            <p className="text-gray-600 mt-2">
                Speak or upload your voice — watch it translate to ISL signs instantly.
            </p>
        </motion.div>
    );
}
