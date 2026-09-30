"use client";

import React, { useState, useEffect, useRef } from "react";
import { useTranslation } from "@/lib/i18n/LanguageContext";
import { api } from "@/lib/api";
import { Mic, MicOff, Volume2, X, Send, Sparkles, AlertCircle } from "lucide-react";

export function VoiceAssistant() {
  const { language, t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [queryText, setQueryText] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<string | null>(null);
  const [speechSupported, setSpeechSupported] = useState(true);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // Check if Web Speech API is supported
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setSpeechSupported(false);
    }
  }, []);

  const getLangCode = () => {
    if (language === "hi") return "hi-IN";
    if (language === "kn") return "kn-IN";
    return "en-IN";
  };

  const startListening = () => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setSpeechSupported(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.lang = getLangCode();
      recognition.interimResults = true;
      recognition.continuous = false;

      recognition.onstart = () => {
        setIsListening(true);
        setResponse(null);
      };

      recognition.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((result: any) => result[0].transcript)
          .join("");
        setQueryText(transcript);
      };

      recognition.onerror = (event: any) => {
        console.warn("Speech recognition error:", event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (e) {
      console.error("Failed to start speech recognition:", e);
      setIsListening(false);
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
  };

  const submitQuery = async () => {
    if (!queryText.trim()) return;
    setLoading(true);
    setResponse(null);
    try {
      const res = await api.voiceQuery(queryText, language);
      setResponse(res.answer);
      // Auto-speak answer if available
      speakText(res.answer);
    } catch (err: any) {
      setResponse("Sorry, could not process your query at this moment. Please check network connection.");
    } finally {
      setLoading(false);
    }
  };

  const speakText = (text: string) => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = getLangCode();
      utterance.rate = 0.95;
      window.speechSynthesis.speak(utterance);
    }
  };

  const sampleQuestions = {
    en: [
      "Should I water my tomatoes today?",
      "What is the soil moisture in North field?",
      "Are there any active alerts?"
    ],
    hi: [
      "क्या आज टमाटर को पानी देना चाहिए?",
      "उत्तर खेत में मिट्टी की नमी कितनी है?",
      "क्या कोई सक्रिय चेतावनी है?"
    ],
    kn: [
      "ಇಂದು ಟೊಮೆಟೊ ಬೆಳೆಗೆ ನೀರು ಹಾಕಬೇಕೇ?",
      "ಉತ್ತರ ಜಮೀನಿನ ತೇವಾಂಶ ಎಷ್ಟು?",
      "ಯಾವುದಾದರೂ ಎಚ್ಚರಿಕೆ ಇದೆಯೇ?"
    ]
  };

  const currentSamples = sampleQuestions[language] || sampleQuestions.en;

  return (
    <>
      {/* Floating Trigger Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-20 md:bottom-8 right-5 z-40 bg-farm-primary hover:bg-farm-emerald text-white p-3.5 rounded-full shadow-2xl flex items-center justify-center border-2 border-farm-leaf group hover:scale-110 active:scale-95 transition-all"
        aria-label="Open Voice Assistant"
      >
        <Mic className="w-6 h-6 text-white group-hover:animate-bounce" />
        <span className="hidden sm:inline-block ml-2 text-xs font-bold pr-1">
          {t("voice_query")}
        </span>
      </button>

      {/* Voice Assistant Modal */}
      {isOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-farm-light animate-in fade-in zoom-in-95 duration-200">
            {/* Header */}
            <div className="flex items-center justify-between pb-4 border-b border-gray-100">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 rounded-xl bg-farm-light text-farm-primary">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-farm-dark leading-tight">
                    {t("voice_assistant_title")}
                  </h3>
                  <span className="text-xs text-gray-500">
                    {language === "hi" ? "हिंदी" : language === "kn" ? "ಕನ್ನಡ" : "English"} • Sarvam & AI Engine
                  </span>
                </div>
              </div>
              <button
                onClick={() => {
                  stopListening();
                  setIsOpen(false);
                }}
                className="p-1.5 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Mic State / Action Area */}
            <div className="py-6 flex flex-col items-center justify-center text-center">
              <button
                onClick={isListening ? stopListening : startListening}
                className={`w-20 h-20 rounded-full flex items-center justify-center shadow-xl transition-all ${
                  isListening
                    ? "bg-farm-dry text-white animate-pulse scale-105 ring-4 ring-red-200"
                    : "bg-farm-primary hover:bg-farm-emerald text-white hover:scale-105"
                }`}
                aria-label={isListening ? t("stop_recording") : t("start_recording")}
              >
                {isListening ? <MicOff className="w-9 h-9" /> : <Mic className="w-9 h-9" />}
              </button>
              <p className="mt-3 text-sm font-semibold text-gray-700">
                {isListening ? t("listening") : t("start_recording")}
              </p>
              <p className="text-xs text-gray-500 max-w-xs mt-1">
                {t("voice_prompt")}
              </p>
            </div>

            {!speechSupported && (
              <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-xl flex items-center space-x-2 text-xs text-amber-800">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{t("voice_unsupported")}</span>
              </div>
            )}

            {/* Recognized / Editable Text Input */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-gray-600 block">
                {t("recognized_text")}
              </label>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={queryText}
                  onChange={(e) => setQueryText(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && submitQuery()}
                  placeholder={currentSamples[0]}
                  className="flex-1 px-3.5 py-2.5 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-farm-emerald text-sm"
                />
                <button
                  onClick={submitQuery}
                  disabled={loading || !queryText.trim()}
                  className="px-4 py-2.5 bg-farm-primary hover:bg-farm-emerald disabled:bg-gray-300 text-white font-semibold rounded-xl text-sm flex items-center space-x-1.5 transition"
                >
                  <Send className="w-4 h-4" />
                  <span className="hidden sm:inline">{t("send_query")}</span>
                </button>
              </div>
            </div>

            {/* Quick Sample Questions */}
            <div className="mt-3 flex flex-wrap gap-1.5">
              {currentSamples.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setQueryText(q);
                  }}
                  className="text-[11px] bg-farm-light/60 hover:bg-farm-light text-farm-dark px-2.5 py-1 rounded-lg transition border border-farm-leaf/20"
                >
                  {q}
                </button>
              ))}
            </div>

            {/* AI Response Display */}
            {(response || loading) && (
              <div className="mt-4 p-4 rounded-xl bg-farm-sand border border-farm-light animate-in fade-in">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-farm-primary flex items-center space-x-1">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>{t("ai_tip")}</span>
                  </span>
                  {response && (
                    <button
                      onClick={() => speakText(response)}
                      className="p-1 rounded-lg text-farm-primary hover:bg-farm-light transition flex items-center space-x-1 text-xs"
                      title={t("speak_answer")}
                    >
                      <Volume2 className="w-4 h-4" />
                      <span className="text-[11px]">{t("speak_answer")}</span>
                    </button>
                  )}
                </div>
                {loading ? (
                  <div className="flex items-center space-x-2 text-sm text-gray-500 py-2">
                    <div className="w-4 h-4 border-2 border-farm-leaf border-t-transparent rounded-full animate-spin"></div>
                    <span>{t("loading")}</span>
                  </div>
                ) : (
                  <p className="text-sm text-gray-800 leading-relaxed font-medium">
                    {response}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
