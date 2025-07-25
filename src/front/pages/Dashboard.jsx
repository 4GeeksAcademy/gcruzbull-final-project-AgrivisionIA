import React, { useState, useEffect } from "react";
import { Navbar } from "../components/Navbar";
import useGlobalReducer from "../hooks/useGlobalReducer";


export const Dashboard = () => {

    const { store, dispatch } = useGlobalReducer();

    const getDashboard = async () => {

        const urlBackend = import.meta.env.VITE_BACKEND_URL;
        // const token = localStorage.getItem("token");
        const token = store.token;

        if (!token) {
            alert("Debes iniciar sesión para acceder al dashboard.");
            return;
        }

        try {
            const response = await fetch(`${urlBackend}/api/dashboard`, {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                },
            });
            const data = await response.json();

            if (response.ok) {
                dispatch({ type: "set_dashboard", payload: data.message });
            } else {
                console.error("Error del backend:", data);
                alert("Error al obtener la información:" + (data?.message || response.statusText));
            }
        } catch (error) {
            if (error.message) throw new Error(
                `Comuniquese con soporte por favor`
            );
        }
    };

    useEffect(() => {
        getDashboard();
    }, []);

    return (
        <div className="min-vh-100 bg-light">
            <div className="container py-5">
                <div className="mx-auto" style={{ maxWidth: "900px" }} >
                    <h1 className="text-center display-6 fw-bold text-dark mb-4">
                        Dashboard
                    </h1>
                </div>

                <div className="mx-auto p-4 text-start bg-white shadow-sm rounded-4">
                    <div className="col-md-12 mb-3">
                        {/* <div> */}
                            <p className=" text-secondary">
                            {store.dashboard || "Bienvenido a tu dashboard de Agrovision IA! Acá podrás ver el análisis del historial de tu huerto, reportes guardados, y configuraciones de cuenta."}
                            </p>
                        {/* </div> */}
                    </div>
                </div>
            </div>
        </div>
    )
};