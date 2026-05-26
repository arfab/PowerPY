-- MontagneAdministracionTest.dbo.dimAnios definition

-- Drop table

-- DROP TABLE MontagneAdministracionTest.dbo.dimAnios;

CREATE TABLE dimAnios (
	codigo nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	descripcion nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL
);


-- MontagneAdministracionTest.dbo.dimBancos definition

-- Drop table

-- DROP TABLE MontagneAdministracionTest.dbo.dimBancos;

CREATE TABLE dimBancos (
	codigo int NOT NULL,
	descripcion nvarchar(100) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL
);


-- MontagneAdministracionTest.dbo.dimColores definition

-- Drop table

-- DROP TABLE MontagneAdministracionTest.dbo.dimColores;

CREATE TABLE dimColores (
	codigo nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	color nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL
);


-- MontagneAdministracionTest.dbo.dimCuotas definition

-- Drop table

-- DROP TABLE MontagneAdministracionTest.dbo.dimCuotas;

CREATE TABLE dimCuotas (
	codigo int NOT NULL,
	descripcion nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL
);


-- MontagneAdministracionTest.dbo.dimDiasSemana definition

-- Drop table

-- DROP TABLE MontagneAdministracionTest.dbo.dimDiasSemana;

CREATE TABLE dimDiasSemana (
	codigo int NOT NULL,
	descripcion nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL
);


-- MontagneAdministracionTest.dbo.dimFranjasHorarias definition

-- Drop table

-- DROP TABLE MontagneAdministracionTest.dbo.dimFranjasHorarias;

CREATE TABLE dimFranjasHorarias (
	codigo int NOT NULL,
	descripcion nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL
);


-- MontagneAdministracionTest.dbo.dimFranquicias definition

-- Drop table

-- DROP TABLE MontagneAdministracionTest.dbo.dimFranquicias;

CREATE TABLE dimFranquicias (
	codigo int NOT NULL,
	descripcion nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL
);


-- MontagneAdministracionTest.dbo.dimGenericos definition

-- Drop table

-- DROP TABLE MontagneAdministracionTest.dbo.dimGenericos;

CREATE TABLE dimGenericos (
	codigo nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	descripcion nvarchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	genero nvarchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	rubro nvarchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	subrubro nvarchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	CONSTRAINT dimGenericos_pk PRIMARY KEY (codigo)
);


-- MontagneAdministracionTest.dbo.dimGeneros definition

-- Drop table

-- DROP TABLE MontagneAdministracionTest.dbo.dimGeneros;

CREATE TABLE dimGeneros (
	codigo nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	descripcion nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL
);


-- MontagneAdministracionTest.dbo.dimLocales definition

-- Drop table

-- DROP TABLE MontagneAdministracionTest.dbo.dimLocales;

CREATE TABLE dimLocales (
	codigo int NOT NULL,
	descripcion nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL
);


-- MontagneAdministracionTest.dbo.dimMeses definition

-- Drop table

-- DROP TABLE MontagneAdministracionTest.dbo.dimMeses;

CREATE TABLE dimMeses (
	codigo int NOT NULL,
	descripcion nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL
);


-- MontagneAdministracionTest.dbo.dimProductos definition

-- Drop table

-- DROP TABLE MontagneAdministracionTest.dbo.dimProductos;

CREATE TABLE dimProductos (
	codigo nvarchar(100) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	descripcion nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	detalle nvarchar(150) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	genero nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	rubro nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	subrubro nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL
);


-- MontagneAdministracionTest.dbo.dimRegiones definition

-- Drop table

-- DROP TABLE MontagneAdministracionTest.dbo.dimRegiones;

CREATE TABLE dimRegiones (
	codigo nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	descripcion nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL
);


-- MontagneAdministracionTest.dbo.dimRubros definition

-- Drop table

-- DROP TABLE MontagneAdministracionTest.dbo.dimRubros;

CREATE TABLE dimRubros (
	codigo nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	descripcion nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL
);


-- MontagneAdministracionTest.dbo.dimSocios definition

-- Drop table

-- DROP TABLE MontagneAdministracionTest.dbo.dimSocios;

CREATE TABLE dimSocios (
	codigo int NOT NULL,
	descripcion nvarchar(150) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL
);


-- MontagneAdministracionTest.dbo.dimSubrubros definition

-- Drop table

-- DROP TABLE MontagneAdministracionTest.dbo.dimSubrubros;

CREATE TABLE dimSubrubros (
	codigo nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	descripcion nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	rubro nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL
);


-- MontagneAdministracionTest.dbo.dimVendedores definition

-- Drop table

-- DROP TABLE MontagneAdministracionTest.dbo.dimVendedores;

CREATE TABLE dimVendedores (
	codigo int NOT NULL,
	descripcion nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL
);


-- MontagneAdministracionTest.dbo.factProductos definition

-- Drop table

-- DROP TABLE MontagneAdministracionTest.dbo.factProductos;

CREATE TABLE factProductos (
	fecha date NULL,
	anio int NULL,
	mes int NULL,
	dia int NULL,
	franja int NULL,
	empresa int NULL,
	tipo_empresa nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	region nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	vendedor int NULL,
	cliente nvarchar(150) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	nrosocio nvarchar(10) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	formulario nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	generico nvarchar(100) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	codalfa nvarchar(15) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	rubro nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	subrubro nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	genero nvarchar(20) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	temporada nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	cantidad int NULL,
	numero_ventas int NULL
);


-- MontagneAdministracionTest.dbo.factVentas definition

-- Drop table

-- DROP TABLE MontagneAdministracionTest.dbo.factVentas;

CREATE TABLE factVentas (
	fecha date NULL,
	anio int NULL,
	mes int NULL,
	dia int NULL,
	franja int NULL,
	empresa int NULL,
	tipo_empresa nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	region nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	vendedor int NULL,
	cliente nvarchar(150) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	nrosocio nvarchar(10) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	formulario nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	monto decimal(16,2) NULL,
	efectivo decimal(16,2) NULL,
	tarjeta decimal(16,2) NULL,
	cheque decimal(16,2) NULL,
	valores decimal(16,2) NULL,
	cantidad int NULL
);