import React, { useEffect } from "react"
import useGlobalReducer from "../hooks/useGlobalReducer.jsx";

export const Home = () => {

	const { store, dispatch } = useGlobalReducer()

	const loadMessage = async () => {
		try {
			const backendUrl = import.meta.env.VITE_BACKEND_URL

			if (!backendUrl) throw new Error("VITE_BACKEND_URL is not defined in .env file")

			const response = await fetch(backendUrl + "/api/hello")
			const data = await response.json()

			if (response.ok) dispatch({ type: "set_hello", payload: data.message })

			return data

		} catch (error) {
			if (error.message) throw new Error(
				`Could not fetch the message from the backend.
				Please check if the backend is running and the backend port is public.`
			);
		}

	}

	useEffect(() => {
		loadMessage()
	}, [])

	return (

		<div>
			{/* contenedor 1 */}
			<div className="bg-green-gradient p-5">
				{/* sub contenedor 1 */}
				<div className="text-center pb-3">
					<h1><span className="fw-bold text-dark fs-8 px-2">AgriVision AI</span></h1>
				</div>
				{/* sub contenedor 2 */}
				<div className="fw-bold text-center pb-3">
					<h1>Transforma tu agricultura con</h1>
					<h1 className="text-success">Inteligencia Artificial</h1>
				</div>
				{/* sub contenedor 3 */}
				<div className="p-4">
					<p className = "fw-bold text-center pb-3">
						Sube imágenes satelitales, aereas, o terrestres de tu campo y obtén un análisis y recomendaciones precisas optimizar tus operacion y disminuir tus costos.
					</p>
					<p className = "fw-bold text-center">
						Análisis y recomendaciones precisas a nivel general y por cuartel sobre la salud, vigor, y estado nutricionals de tu huerto.
					</p>
				</div>
				{/* sub contenedor 4 */}
				{/* <div className="d-flex justify-content-center align-content-center mt-3">
					<button className="rounded-3 me-4 btn btn-succes bg-success text-white fw-bold border border-success-subtle">
						Comenzar Análisis Gratuito
					</button>
					<button className="d-flex align-content-center rounded-3 ms-4 btn btn-white border fw-bold border-secondary-subtle">
						<i className="fs-4 my-2 py-auto px-2 fa-regular fa-square-caret-right"></i>
						<p className="align-content-center my-1 pt-0 pe-1">Ver Demo</p>
					</button>
				</div> */}
				{/* sub contenedor 5 */}
				<div className="container">
					<div className="row d-flex justify-content-center align-items-center row-gap-3 " style={{ gridTemplateColumns: '1fr 1fr' }}>
						
						<button className="col-md-12 col-lg-4 d-flex align-content-center rounded-5 me-1 btn btn-white fw-bold border border-secondary-subtle">
							<i className="fa-2x p-3 fas fa-tree" style={{color: "#11a736"}}></i> 
							<p className="m-auto">Detección de Deficiencias Nutricionales</p>
						</button>

						<button className="col-md-12 col-lg-4 d-flex align-content-center rounded-5 ms-1 btn btn-white fw-bold border border-secondary-subtle">
							<i className="fa-2x p-3 fa-solid fa-bug" style={{color: "#948800"}}></i>
							<p classNasme="m-auto">Detección de Plagas y Patógenos</p>
						</button>

						<button className="col-md-12 col-lg-4 d-flex align-content-center rounded-5 me-1 btn btn-white fw-bold border border-secondary-subtle">
							<i className="fa-2x p-3 fa-solid fa-map-location-dot" style={{color: "#0b6e24ff"}}></i>
							<p className="m-auto p-3">Análisis General y por Cuartel</p>
						</button>

						<button className="col-md-12 col-lg-4 d-flex align-content-center rounded-5 ms-1 btn btn-white fw-bold border border-secondary-subtle">
							<i className="fa-2x p-3 fa-sharp fa-solid fa-chart-simple" style={{color: "#1d5ecd"}}></i>
							<p className="m-auto p-3">Análisis de Vigor del Huerto</p>
						</button>

					</div>
				</div>
			</div>

			<div className="mx-auto container">
				<div className="row">
					{/* contenedor 2 */}
					<div className="col-md-12 col-lg-12 text-center my-4 py-5 border shadow rounded-4 ">
						<div className="d-flex justify-content-center align-content-center">
							<i className="p-4 pt-0 fa-2x fa-solid fa-file-invoice" style={{color: "#1f9bf9"}}></i>
							<h3>Resultados del Análisis</h3>
						</div>
						<p className="mb-3">
							Sube una imagen para ver el análisis detallado del cultivo
						</p>
						<div>
							<label htmlFor="btnUpload" className="form-label d-flex">
								<i className="fs-4 m-2 fa-solid fa-cloud-arrow-up" style={{color: "#3fabfd"}}></i>
								<h5 className="m-2">Subir Imagen</h5>
							</label>
                            <input
                                type="file"
                                className="form-control border-primary m-auto"
                                id="btnUpload"
                                placeholder="Cargar Imágen"
                                name="uploadImage"
											
                                // onChange={handleInputChange}
                                // value={}
                            />
						</div>
						
					</div>
					
				</div>

				<div className="col-sm-12 col-md-12 text-center m-auto my-5">
					<h1>¿Por qué elegir AgriVision AI?</h1>
					<p>
						Nuestra plataforma combina tecnología IA de vanguardia con experiencia agrícola para ayudarte a tomar decisiones basadas en datos.
					</p>
				</div>
				

				{/* contenedor 5 */}
				<div className="mx-auto container" >
						<div className="d-grid gap-0 row-gap-3 column-gap-3" style={{ gridTemplateColumns: '1fr 1fr' }}>
							<div className="col-sm-6 col-md-12 text-center p-5 border rounded-4 shadow">
								<i className="fa-2x fa-regular fa-file-image" style={{color: "#0ca145"}}></i>
								<h3>Análisis Multi-Fuente</h3>
								<p>
									Soporte para imágenes de drones, datos satelitales y fotografía terrestre para un análisis integral del campo.
								</p>
							</div>

							<div className="col-sm-6 col-md-12 text-center p-5 border rounded-4 shadow">
								<i className="fa-2x fa-sharp fa-solid fa-magnifying-glass-chart" style={{color: "#075ae9"}}></i>
								<h3>IA Avanzada</h3>
								<p>
									Algoritmos de aprendizaje automático detectan estrés en cultivos, enfermedades y patrones de crecimiento con alta precisión.
								</p>
							</div>

							<div className="col-sm-6 col-md-12 text-center p-5 border rounded-4 shadow">
								<i className="fa-2x fa-solid fa-leaf" style={{color: "#0fe656"}}></i>
								<h3>Recomendaciones Precisas</h3>
								<p>
									Obtén recomendaciones específicas y accionables para estrategias de riego, fertilización y manejo de plagas.
								</p>
							</div>

							<div className="col-sm-6 col-md-12 text-center p-5 border rounded-4 shadow">
								<i className="fa-2x fa-sharp fa-solid fa-chart-area" style={{color: "#3a1b98"}}></i>
								<h3>Análisis de Tendencias</h3>
								<p>
									Monitorea el progreso de tus cultivos a lo largo del tiempo con reportes detallados y análisis comparativos.
								</p>
							</div>

							<div className="col-sm-6 col-md-12 text-center p-5 border rounded-4 shadow">
								<i className="fa-2x fa-sharp fa-solid fa-shield" style={{color: "#ff0000"}}></i>
								<h3>Detección Temprana</h3>
								<p>
									Identifica problemas antes de que se vuelvan críticos, ahorrando tiempo y recursos valiosos.
								</p>
							</div>

							<div className="col-sm-6 col-md-12 text-center p-5 border rounded-4 shadow">
								<i className="fa-2x fa-sharp fa-solid fa-bolt" style={{color: '#FFD43B'}}></i>
								<h3>Resultados Instantáneos</h3>
								<p>
									Obtén análisis completos en segundos, no en días. Toma decisiones informadas al instante.
								</p>
							</div>
						</div>
				</div>
			</div>
		</div>

	);
};