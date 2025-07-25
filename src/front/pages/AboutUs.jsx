import React, { useState, useEffect } from "react";
import { Navbar } from "../components/Navbar";
import useGlobalReducer from "../hooks/useGlobalReducer";


export const AboutUs = () => {

    const { store, dispatch } = useGlobalReducer();

    const getAboutUs = async () => {

        const urlBackend = import.meta.env.VITE_BACKEND_URL;

        try {
            const response = await fetch(`${urlBackend}/api/about-us`);
            const data = await response.json();

            if (response.ok) {
                dispatch({ type: "set_about", payload: data.message });
            } else {
                alert("Error al obtener la información:", data?.message || response.statusText);
            }
        } catch (error) {
            if (error.message) throw new Error(
				`Comuniquese con soporte por favor`
			);
        }
    };

    useEffect(() => {
        getAboutUs();
    }, []);

    return (
        <div className="min-vh-100 bg-light">
            <div className="container py-5">
                <div className="mx-auto" style={{ maxWidth: "900px" }} >
                    <h1 className="text-center display-6 fw-bold text-dark mb-5">
                        Sobre AgriVision AI
                    </h1>
                </div>

                <div className="row g-4 mb-5 text-center">
                    <div className="col-md-6">
                        <div className="bg-white shadow-sm rounded-4 p-4 h-100">
                            <div className="text-success mb-3 fs-1">
                                <i className="fas fa-bullseye"></i>
                            </div>
                            <h3 className="fs-5 fw-semibold text-dark mb-3">Misión</h3>
                            <p className="text-secondary">
                                Mediante el uso de Inteligencia Artificial y análisis de datos, ayudar a los medianos y pequeños agricultores a aumentar la eficiencia de sus operaciones tomando decisiones en base a insights obtenidos de datos concretos.
                            </p>
                        </div>
                    </div>

                    <div className="col-md-6">
                        <div className="bg-white shadow-sm rounded-4 p-4 h-100">
                            <div className="text-success mb-3 fs-1">
                                <i className="fas fa-leaf"></i>
                            </div>
                            <h3 className="fs-5 fw-semibold text-dark mb-3">Tecnología</h3>
                            <p className="text-secondary">
                                Nuestra plataforma, mediante algoritmos avanzados de machine learning y análisis de datos, analiza imágenes de drones, datos satelitales y fotografía terrestre para brindar insights
                                sobre el vigor del huerto, deficiencias nutricionales, y estado de salud y estrategias de control de plagas.
                            </p>
                        </div>
                    </div>

                    <div className="col-md-12 bg-white shadow-sm rounded-4 p-5">
                        <h2 className="h4 fw-bold text-dark mb-3">Nuestra Historia</h2>
                        <p className="text-secondary mb-3">
                            AgriVision AI nació con la visión de hacer que la agricultura de precisión sea accesible para agricultores de todos los tamaños.
                            Combinamos inteligencia artificial de vanguardia con la experiencia práctica agrícola de nuestros profesionales para ayudar a tomar decisiones basadas en datos.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
};