import { Link, useNavigate } from "react-router-dom";
import useGlobalReducer from "../hooks/useGlobalReducer";

export const Navbar = () => {

	const { dispatch, store } = useGlobalReducer();

	const navigate = useNavigate();

	const isAuthenticated = store.token && store.userData?.email;

	const userData = store.userData; // aquí estará full_name y avatar

	const handleLogout = () => {
		const confirmLogout = window.confirm("¿Estás seguro que quieres cerrar sesión?");

		if (confirmLogout) {
			localStorage.removeItem("token");
			dispatch({ type: "logout" });
			navigate("/login");
			alert("Sesión cerrada exitosamente");
		}
	};

	return (
		<nav className="navbar navbar-expand-md navbar-light bg-white border-bottom shadow-sm sticky-top">
			<div className="container w-100">
				{/* Contenedor 1: Logo */}
				<Link to="/" className="navbar-brand d-flex align-items-center">
					<div className="p-2 bg-white me-2 d-flex align-items-center justify-content-center">
						<i className="fas fa-leaf fa-2x text-success mb-2"></i>
					</div>
					<div className="d-flex align-items-baseline">
						<span className="fs-4 fw-bold text-dark">AgriVision</span>
						<span className="fs-5 fw-medium text-success ms-1">AI</span>
					</div>
				</Link>

				{/* Botón hamburguesa para celulares */}
				<button
					className="navbar-toggler"
					type="button"
					data-bs-toggle="collapse"
					data-bs-target="#navbarNav"
					aria-controls="navbarNav"
					aria-expanded="false"
					aria-label="Toggle navigation"
				>
					<span className="navbar-toggler-icon"></span>
				</button>

				{/* Contenido colapsable */}
				<div className="collapse navbar-collapse" id="navbarNav">
					{/* Enlaces de navegación */}
					<ul className="navbar-nav ms-auto mb-2 mb-md-0 me-3">
						<li className="nav-item mx-3">
							<Link to="/" className="nav-link text-dark fw-bold">
								Inicio
							</Link>
						</li>
						<li className="nav-item mx-3">
							<Link to="/dashboard" className="nav-link text-dark fw-bold">
								Dashboard
							</Link>
						</li>
						<li className="nav-item mx-3">
							<Link to="/about-us" className="nav-link text-dark fw-bold">
								Nosotros
							</Link>
						</li>
					</ul>

					{/* Botones de autenticación */}
					<div className="d-flex align-items-center gap-2">
						{!isAuthenticated ? (
							<>
								<Link to="/login" className="d-flex btn btn-outline-secondary me-3 my-3 p-1">
									<span className="d-flex px-2 py-1">
										<i className="fa-solid px-2 pt-1 fa-arrow-right-to-bracket"></i>
										<p className="text-black fw-bold mb-0 pe-2">Ingresar</p>
									</span>
								</Link>
							</>
						) : (
							<>
								{/* NUEVO: Dropdown con perfil y logout */}
								<div className="dropdown">
									<button
										className="btn btn-light dropdown-toggle d-flex align-items-center"
										type="button"
										id="userDropdown"
										data-bs-toggle="dropdown"
										aria-expanded="false"
									>
										<img
											src={userData?.avatar || "https://avatar.iran.liara.run/public/4"}
											alt="Avatar"
											className="rounded-circle me-2"
											style={{ width: "32px", height: "32px", objectFit: "cover" }}
										/>
										<span className="fw-bold">{userData?.full_name || "Usuario"}</span>
									</button>
									
									<ul className="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
										<li>
											<h6 className="dropdown-header">
												{userData?.is_admin === 'admin' ? '👑 Administrador' : '👤 Usuario'}
											</h6>
										</li>
										<li><hr className="dropdown-divider" /></li>
										<li>
											<Link className="dropdown-item" to="/profile">
												<i className="fas fa-user me-2"></i>Mi Perfil
											</Link>
										</li>
										<li>
											<Link className="dropdown-item" to="/dashboard">
												<i className="fas fa-tachometer-alt me-2"></i>Dashboard
											</Link>
										</li>
										{userData?.is_admin === 'admin' && (
											<>
												<li><hr className="dropdown-divider" /></li>
												<li>
													<span className="dropdown-item-text">
														<i className="fas fa-crown me-2 text-warning"></i>
														<strong>Panel Admin</strong>
													</span>
												</li>
											</>
										)}
										<li><hr className="dropdown-divider" /></li>
										<li>
											<button 
												className="dropdown-item text-danger" 
												onClick={handleLogout}
											>
												<i className="fas fa-sign-out-alt me-2"></i>Cerrar Sesión
											</button>
										</li>
									</ul>
								</div>
							</>
						)}
					</div>
				</div>
			</div>
		</nav>
	);
};



// 	return (
// 		<nav className="navbar navbar-expand-md navbar-light bg-white border-bottom shadow-sm sticky-top">
// 			<div className="container w-100">

// 				{/* Contenedor 1: Logo */}
// 				<Link to="/" className="navbar-brand d-flex align-items-center">
// 					<div className="p-2 bg-white me-2 d-flex align-items-center justify-content-center">
// 						<i className="fas fa-leaf fa-2x text-success mb-2"></i>
// 					</div>
// 					<div className="d-flex align-items-baseline">
// 						<span className="fs-4 fw-bold text-dark">AgriVision</span>
// 						<span className="fs-5 fw-medium text-success ms-1">AI</span>
// 					</div>
// 				</Link>

// 				{/* Botón hamburguesa para celulares */}
// 				<button
// 					className="navbar-toggler"
// 					type="button"
// 					data-bs-toggle="collapse"
// 					data-bs-target="#navbarNav"
// 					aria-controls="navbarNav"
// 					aria-expanded="false"
// 					aria-label="Toggle navigation"
// 				>
// 					<span className="navbar-toggler-icon"></span>
// 				</button>

// 				{/* Contenido colapsable */}
// 				<div className="collapse navbar-collapse" id="navbarNav">
// 					{/* Enlaces de navegación */}
// 					<ul className="navbar-nav ms-auto mb-2 mb-md-0 me-3">
// 						<li className="nav-item mx-3">
// 							<Link to="/" className="nav-link text-dark fw-bold">
// 								Inicio
// 							</Link>
// 						</li>
// 						<li className="nav-item mx-3">
// 							<Link to="/dashboard" className="nav-link text-dark fw-bold">
// 								Dashboard
// 							</Link>
// 						</li>
// 						<li className="nav-item mx-3">
// 							<Link to="/about-us" className="nav-link text-dark fw-bold">
// 								Nosotros
// 							</Link>
// 						</li>
// 					</ul>

// 					{/* Botones de autenticación */}
// 					{/* <div className="d-flex align-items-center gap-2">
// 						<Link to="/login" className="d-flex btn btn-outline-secondary me-3 my-3 p-1">
// 							<span className="d-flex px-2 py-1">
// 								<i className="fa-solid px-2 pt-1 fa-arrow-right-to-bracket"></i>
// 								<p className="text-black fw-bold mb-0 pe-2">Ingresar</p>
// 							</span>	
// 						</Link>
// 						<Link to="/profile" className="d-flex btn btn-success ms-2 my-3 text-white align-content-center">
// 							<span className="px-2 mb-1"><p className="fw-bold mb-0 pe-2">Perfil</p></span>
// 						</Link>
// 					</div> */}
// 					<div className="d-flex align-items-center gap-2">
// 						{!isAuthenticated ? (
// 							<>
// 								<Link to="/login" className="d-flex btn btn-outline-secondary me-3 my-3 p-1">
// 									<span className="d-flex px-2 py-1">
// 										<i className="fa-solid px-2 pt-1 fa-arrow-right-to-bracket"></i>
// 										<p className="text-black fw-bold mb-0 pe-2">Ingresar</p>
// 									</span>
// 								</Link>
// 							</>
// 						) : (
// 							<>
// 								<Link to="/profile" className="d-flex align-items-center text-decoration-none">
// 									<img
// 										src={userData?.avatar || "https://avatar.iran.liara.run/public/4"}
// 										alt="Avatar"
// 										className="rounded-circle"
// 										style={{ width: "40px", height: "40px", objectFit: "cover", marginRight: "10px" }}
// 									/>
// 									<span className="fw-bold text-dark">{userData?.full_name || "Perfil"}</span>
// 								</Link>
// 							</>
// 						)}
// 					</div>

// 				</div>
// 			</div>
// 		</nav>		
// 	);
// };