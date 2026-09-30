"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useTranslation } from "@/lib/i18n/LanguageContext";
import { api } from "@/lib/api";
import { FieldDetail } from "@/types";
import { MoistureGauge } from "@/components/MoistureGauge";
import {
  Plus, Edit, Trash2, ArrowRight, X, Trees, Check, AlertTriangle
} from "lucide-react";

export default function FieldsPage() {
  const { t } = useTranslation();
  const [fields, setFields] = useState<FieldDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState<string | null>(null);

  // Form State for Add / Edit
  const [formData, setFormData] = useState({
    id: "",
    name: "",
    crop_type: "tomato",
    growth_stage: "vegetative",
    soil_type: "loam",
    area_acres: 2.5,
    location: "Main Farm",
    target_moisture_min: 35.0,
    target_moisture_max: 70.0
  });

  const loadFields = async () => {
    try {
      setLoading(true);
      const data = await api.getFields();
      setFields(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFields();
  }, []);

  const handleCreateField = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createField(formData);
      setShowAddModal(false);
      setFormData({
        id: "",
        name: "",
        crop_type: "tomato",
        growth_stage: "vegetative",
        soil_type: "loam",
        area_acres: 2.5,
        location: "Main Farm",
        target_moisture_min: 35.0,
        target_moisture_max: 70.0
      });
      await loadFields();
    } catch (err: any) {
      alert(`Error creating field: ${err.message || "Failed to create"}`);
    }
  };

  const handleDeleteField = async (id: string) => {
    try {
      await api.deleteField(id);
      setShowDeleteModal(null);
      await loadFields();
    } catch (err: any) {
      alert(`Error deleting field: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
            {t("field_management")}
          </h1>
          <p className="text-xs sm:text-sm text-gray-500">
            Configure your agricultural plots, target soil moisture thresholds, and telemetry
          </p>
        </div>

        <button
          onClick={() => {
            const randomId = `field_${Date.now().toString().slice(-4)}`;
            setFormData({ ...formData, id: randomId });
            setShowAddModal(true);
          }}
          className="px-4 py-2.5 bg-farm-primary hover:bg-farm-emerald text-white font-bold rounded-xl text-xs sm:text-sm flex items-center space-x-1.5 shadow-md transition self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>{t("add_new_field")}</span>
        </button>
      </div>

      {/* Fields List */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-60 bg-gray-200 animate-pulse rounded-2xl"></div>
          ))}
        </div>
      ) : fields.length === 0 ? (
        <div className="bg-white p-12 text-center rounded-2xl border border-dashed border-gray-300">
          <Trees className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-600 font-semibold text-sm">No fields found.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {fields.map((field) => (
            <div
              key={field.id}
              className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-[10px] font-bold tracking-wider uppercase text-farm-emerald bg-farm-light px-2 py-0.5 rounded-md">
                      {field.crop_type} • {field.growth_stage}
                    </span>
                    <h3 className="text-lg font-bold text-gray-900 mt-1">
                      {field.name}
                    </h3>
                    <p className="text-xs text-gray-500">
                      {field.location || "Sector A"} • {field.area_acres} Acres • {field.soil_type}
                    </p>
                  </div>

                  <button
                    onClick={() => setShowDeleteModal(field.id)}
                    className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
                    title={t("delete_field")}
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="my-4">
                  <MoistureGauge
                    value={field.latest_soil_moisture ?? 35}
                    minTarget={field.target_moisture_min}
                    maxTarget={field.target_moisture_max}
                  />
                </div>
              </div>

              <div className="pt-3 border-t border-gray-100 flex items-center justify-between">
                <span className="text-xs text-gray-500">
                  ID: <code className="font-mono text-farm-dark">{field.id}</code>
                </span>
                <Link
                  href={`/fields/${field.id}`}
                  className="text-xs font-bold text-farm-dark hover:text-farm-emerald flex items-center space-x-1 group/link"
                >
                  <span>{t("view_details")}</span>
                  <ArrowRight className="w-3.5 h-3.5 group-hover/link:translate-x-1 transition-transform" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Field Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-farm-light animate-in fade-in duration-150 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-gray-100 mb-4">
              <h3 className="text-lg font-bold text-gray-900 flex items-center space-x-2">
                <Trees className="w-5 h-5 text-farm-primary" />
                <span>{t("add_new_field")}</span>
              </h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="p-1.5 text-gray-400 hover:text-gray-700 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateField} className="space-y-4 text-xs sm:text-sm">
              <div>
                <label className="block font-semibold text-gray-700 mb-1">
                  Field Unique Identifier
                </label>
                <input
                  type="text"
                  required
                  value={formData.id}
                  onChange={(e) => setFormData({ ...formData, id: e.target.value })}
                  placeholder="e.g. north_plot_2"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-farm-emerald focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-gray-700 mb-1">
                  {t("field_name")}
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. North Plot - Tomato"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-farm-emerald focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-gray-700 mb-1">
                    {t("crop_type")}
                  </label>
                  <select
                    value={formData.crop_type}
                    onChange={(e) => setFormData({ ...formData, crop_type: e.target.value })}
                    className="w-full px-3 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-farm-emerald focus:outline-none bg-white"
                  >
                    <option value="tomato">Tomato</option>
                    <option value="lettuce">Lettuce</option>
                    <option value="cotton">Cotton</option>
                    <option value="maize">Maize</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-gray-700 mb-1">
                    {t("growth_stage")}
                  </label>
                  <select
                    value={formData.growth_stage}
                    onChange={(e) => setFormData({ ...formData, growth_stage: e.target.value })}
                    className="w-full px-3 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-farm-emerald focus:outline-none bg-white"
                  >
                    <option value="emergence">Emergence</option>
                    <option value="vegetative">Vegetative</option>
                    <option value="flowering">Flowering</option>
                    <option value="maturity">Maturity</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-gray-700 mb-1">
                    {t("area_acres")}
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0.1"
                    required
                    value={formData.area_acres}
                    onChange={(e) => setFormData({ ...formData, area_acres: parseFloat(e.target.value) || 1 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-farm-emerald focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block font-semibold text-gray-700 mb-1">
                    {t("soil_type")}
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.soil_type}
                    onChange={(e) => setFormData({ ...formData, soil_type: e.target.value })}
                    placeholder="e.g. Loam, Clay, Sandy"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-farm-emerald focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-gray-700 mb-1">
                    {t("min_moisture")}
                  </label>
                  <input
                    type="number"
                    min="10"
                    max="90"
                    required
                    value={formData.target_moisture_min}
                    onChange={(e) => setFormData({ ...formData, target_moisture_min: parseFloat(e.target.value) || 30 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-farm-emerald focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block font-semibold text-gray-700 mb-1">
                    {t("max_moisture")}
                  </label>
                  <input
                    type="number"
                    min="20"
                    max="95"
                    required
                    value={formData.target_moisture_max}
                    onChange={(e) => setFormData({ ...formData, target_moisture_max: parseFloat(e.target.value) || 75 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-farm-emerald focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-gray-700 mb-1">
                  {t("location")}
                </label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  placeholder="e.g. Sector B - East Valley"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-farm-emerald focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2.5 text-gray-600 hover:bg-gray-100 rounded-xl font-semibold"
                >
                  {t("cancel")}
                </button>
                <button
                  type="submit"
                  className="px-5 py-2.5 bg-farm-primary hover:bg-farm-emerald text-white rounded-xl font-bold shadow-md"
                >
                  {t("save_field")}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-red-100 animate-in fade-in">
            <div className="flex items-center space-x-3 text-red-600 mb-3">
              <AlertTriangle className="w-6 h-6" />
              <h3 className="text-lg font-bold">{t("delete_field")}</h3>
            </div>
            <p className="text-sm text-gray-600 mb-6">
              {t("confirm_delete_field")}
            </p>
            <div className="flex items-center justify-end space-x-3">
              <button
                onClick={() => setShowDeleteModal(null)}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-xl text-sm font-semibold"
              >
                {t("cancel")}
              </button>
              <button
                onClick={() => handleDeleteField(showDeleteModal)}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl text-sm font-bold shadow-md"
              >
                {t("confirm")}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
