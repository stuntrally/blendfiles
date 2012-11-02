#include "pch.h"
using namespace std;
using namespace boost;


//  Helper program for trees exported from blender in mesh.xml
//  read all .dae filenames to change *.mesh.xml file names
//  read all Trunk*.mesh.xml and Twig*.mesh.xml (1 tree has Trunk and Twig):
//    Trunk-mesh.176.mesh.xml
//    Twig-mesh.176.mesh.xml
//  change sharedgeom to geom, and put it in submesh
//  change material name to tree10okyTwig, usesharedvertices to false
//  connect both xmls to 1 xml

//  To use Ogre mesh in Paged Geometry, it must not have <sharedgeometry>, only <geometry> in each <submesh>

///  input format (both Trunk* and Twig* files)
/*
<mesh>
    <sharedgeometry vertexcount="1341">
        <vertexbuffer texture_coords="1" positions="true" colours_diffuse="False" normals="true">
            <vertex>
                <position y="1.730701" x="0.148086" z="0.059016"/>
                <normal y="-0.050813" x="0.984863" z="0.165654"/>
                <texcoord u="1.000000" v="-0.662935"/>
            </vertex>
            ...
        </vertexbuffer>
    </sharedgeometry>
    <submeshes>
        <submesh usesharedvertices="true" material="Material.190" use32bitindexes="False">
            <faces count="2672">
                <face v1="0" v2="1" v3="2"/>
                <face v1="1" v2="3" v3="2"/>
                ...
                <face v1="1337" v2="1315" v3="1338"/>
            </faces>
        </submesh>
    </submeshes>
</mesh>
*/
///  output example tree.mesh.xml
/*
	<?xml version="1.0" encoding="UTF-8"?>
	<mesh>
		<submeshes>
			<submesh usesharedvertices="false" material="tree1-tree" use32bitindexes="False">
				<geometry vertexcount="6012">
					<vertexbuffer texture_coords="1" positions="true" colours_diffuse="False" normals="true">
						<vertex>
							<position y="2.447526" x="0.068849" z="-0.124469"/>
							<normal y="0.004133" x="0.623107" z="-0.782126"/>
							<texcoord u="1.000000" v="-0.737758"/>
						</vertex>
						...
					</vertexbuffer>
				</geometry>
				<faces count="2004">
					<face v1="0" v2="1" v3="2"/>
					...
					<face v1="6009" v2="6010" v3="6011"/>
				</faces>
	        </submesh>
		    <submesh usesharedvertices="false" material="tree1-twig" use32bitindexes="False">
		    ...
*/


///  utils

//  error msg, exit
int Exit(string msg, int i=1)
{
	if (i==1)  cout << "Error: ";
	cout << msg << "\n";
	cout << "Press enter to exit.\n";
	getchar();
	return i;
}

string toStr(float f)
{
	ostringstream s;
	s << f;
	return s.str();
}

string toStr(int i)
{
	ostringstream s;
	s << i;
	return s.str();
}

#define toStrC(i)  toStr(i).c_str()

/*
float s2f(const char* s)
{
	stringstream ss(s);
	float f;
	ss >> f;
	return f;
}

int s2i(const char* s)
{
	stringstream ss(s);
	int i;
	ss >> i;
	return i;
}
*/


//  list matching files in directory
//----------------------------------------------------------------------------
vector<string> ListFiles(const char* sPath, const char* sPattern=".*")
{
	regex expr(sPattern);
	vector<string> files;
	try
	{
		filesystem::directory_iterator it(sPath), end_it;

		for (; it != end_it; ++it)
		{
			//  files only
			bool isDir = filesystem::is_directory(it->status());
			if (isDir)  continue;
			
			string name = it->path().filename().string();

			smatch what;
			if (!regex_match(name, what, expr))  continue;

			files.push_back(name);
		}
	}
	catch (const filesystem::filesystem_error& e)
	{
		cout << e.what() << "\n";
		//cout << e.code().message() << "\n";
	}
	return files;
}


//  Load geometry from .mesh.xml (1 submesh only)
//----------------------------------------------------------------------------
int LoadSubmesh(string file,
	vector<string>& vId, vector<string>& vPos, vector<string>& vNorm, vector<string>& vUV)
{
	vId.clear();  vPos.clear();  vNorm.clear();  vUV.clear();
	
	TiXmlDocument doc;
	if (!doc.LoadFile(file.c_str()))  return Exit("Can't read file.");
		
	TiXmlElement* root = doc.RootElement();
	if (!root)  return Exit("No root");

	//  Read
	const char* a=0;
 	TiXmlElement* sgeom = root->FirstChildElement("sharedgeometry");
	if (!sgeom)  return Exit("No sharedgeometry");
	//int count = 0, i = 0;
	//a = sgeom->Attribute("vertexcount");	if (a)  count = atoi(a);  //else
	
	TiXmlElement* vbuf = sgeom->FirstChildElement("vertexbuffer");
	if (!vbuf)  return Exit("No vertexbuffer");

	//  verts
	//-----------------------------------------------------------
	TiXmlElement* vert = vbuf->FirstChildElement("vertex");
	if (!vert)  return Exit("No vertex");

	while (vert)
	{		
		TiXmlElement* pos = vert->FirstChildElement("position");
		if (!pos)  return Exit("No vertex position");

		TiXmlElement* norm = vert->FirstChildElement("normal");
		if (!norm)  return Exit("No vertex normal");

		TiXmlElement* txc = vert->FirstChildElement("texcoord");
		if (!txc)  return Exit("No vertex texcoord");

		a = pos->Attribute("x");	if (a)  vPos.push_back((a));
		a = pos->Attribute("y");	if (a)  vPos.push_back((a));
		a = pos->Attribute("z");	if (a)  vPos.push_back((a));

		a = norm->Attribute("x");	if (a)  vNorm.push_back((a));
		a = norm->Attribute("y");	if (a)  vNorm.push_back((a));
		a = norm->Attribute("z");	if (a)  vNorm.push_back((a));

		a = txc->Attribute("u");	if (a)  vUV.push_back((a));
		a = txc->Attribute("v");	if (a)  vUV.push_back((a));
		
		vert = vert->NextSiblingElement("vertex");
	}

	//  read face indicies
	//-----------------------------------------------------------
 	TiXmlElement* subs = root->FirstChildElement("submeshes");
	if (!subs)  return Exit("No submeshes");
	
	TiXmlElement* sub = subs->FirstChildElement("submesh");
	if (!sub)  return Exit("No submesh");
	
	TiXmlElement* fcs = sub->FirstChildElement("faces");
	if (!fcs)  return Exit("No faces");
	//int count = 0, i = 0;
	//a = fcs->Attribute("count");	if (a)  count = atoi(a);  //else

	TiXmlElement* face = fcs->FirstChildElement("face");
	if (!face)  return Exit("No face");

	while (face)
	{		
		a = face->Attribute("v1");	if (a)  vId.push_back((a));
		a = face->Attribute("v2");	if (a)  vId.push_back((a));
		a = face->Attribute("v3");	if (a)  vId.push_back((a));

		face = face->NextSiblingElement("face");
	}
	return 0;
}


//  Save geometry as submesh in .mesh.xml
//----------------------------------------------------------------------------
void SaveSubmesh(TiXmlElement& subs/*<submeshes>*/, string sMtr,
	vector<string> vId, vector<string> vPos, vector<string> vNorm, vector<string> vUV)
{
	TiXmlElement sub("submesh");
		sub.SetAttribute("material", sMtr.c_str());
		sub.SetAttribute("usesharedvertices", "false");
		sub.SetAttribute("use32bitindexes", "false");

		TiXmlElement faces("faces");
			int cnt = vId.size() / 3, a=0;
			faces.SetAttribute("count", toStrC(cnt));
			
			TiXmlElement face("face");
			for (int i=0; i < cnt; ++i)
			{
				//TiXmlElement face("face");
				face.SetAttribute("v1", vId[a++].c_str());
				face.SetAttribute("v2", vId[a++].c_str());
				face.SetAttribute("v3", vId[a++].c_str());
				faces.InsertEndChild(face);
			}
		sub.InsertEndChild(faces);

		TiXmlElement geo("geometry");
			cnt = vPos.size() / 3;
			geo.SetAttribute("vertexcount", toStrC(cnt));

						TiXmlElement pos("position");
						TiXmlElement norm("normal");
						TiXmlElement texc("texcoord");

			TiXmlElement vbuf("vertexbuffer");
				vbuf.SetAttribute("positions", "true");
				vbuf.SetAttribute("normals", "true");
				vbuf.SetAttribute("texture_coords", "1");
				vbuf.SetAttribute("colours_diffuse", "false");
			
				int ap=0, an=0, at=0;
				for (int i=0; i < cnt; ++i)
				{
					TiXmlElement vert("vertex");
						
						pos.SetAttribute("x", vPos[ap++].c_str());
						pos.SetAttribute("y", vPos[ap++].c_str());
						pos.SetAttribute("z", vPos[ap++].c_str());
						vert.InsertEndChild(pos);
						
						//float nx = vNorm[an++];
						//float ny = vNorm[an++];
						//float nz = vNorm[an++];
						//float len = sqrt(nx*nx+ny*ny+nz*nz);  //normalize
						//nx /= len;  ny /= len;  nz /= len;
						//cout << toStr(nx*nx+ny*ny+nz*nz) << "\n";
						norm.SetAttribute("x", vNorm[an++].c_str());
						norm.SetAttribute("y", vNorm[an++].c_str());
						norm.SetAttribute("z", vNorm[an++].c_str());
						vert.InsertEndChild(norm);
						
						texc.SetAttribute("u", vUV[at++].c_str());
						texc.SetAttribute("v", vUV[at++].c_str());
						vert.InsertEndChild(texc);

					vbuf.InsertEndChild(vert);
				}
			geo.InsertEndChild(vbuf);
		sub.InsertEndChild(geo);
	subs.InsertEndChild(sub);
}


///  main
//---------------------------------------------------------------------------------------------------------------
int _tmain(int argc, _TCHAR* argv[])
{
	//string path = "c:/";
	string path = "./";
	vector<string> vDae   = ListFiles(path.c_str(), ".*\.dae");
	vector<string> vTrunk = ListFiles(path.c_str(), "Trunk.*\.xml");
	vector<string> vTwig  = ListFiles(path.c_str(), "Twig.*\.xml");

	//  same count
	if (vDae.size() != vTrunk.size() || vTrunk.size() != vTwig.size())
		return Exit("Count of files *.dae, Trunk*.xml and Twig*.xml is not the same.");
	if (vDae.size() == 0)
		return Exit("No files (*.dae or Trunk*.xml or Twig*.xml.");


	//  for each tree
	for (int i=0; i < vDae.size(); ++i)
	//for (int i=0; i < 1; ++i)  //test
	{
		const string sTree = vDae[i];  // only name needed from .dae
		const string name = sTree.substr(0,sTree.length()-4);  // tree name, no extension
		const string fileTrunk = vTrunk[i];
		const string fileTwig = vTwig[i];
		cout << "Tree name: "+name+"  "+fileTrunk+", "+fileTwig+"\n";
		

		vector<string> vPos,vNorm,vUV;  //vertex data: pos x3, norm x3, uv x2
		vector<string> vId;  // read face indicies
		
		//  Save .mesh.xml output
		TiXmlDocument oXml;  TiXmlElement oRoot("mesh");
		TiXmlElement subs("submeshes");

		LoadSubmesh(fileTrunk, vId, vPos, vNorm, vUV);
		SaveSubmesh(subs, name+"Trunk", vId, vPos, vNorm, vUV);

		LoadSubmesh(fileTwig, vId, vPos, vNorm, vUV);
		SaveSubmesh(subs, name+"Twig", vId, vPos, vNorm, vUV);

		oRoot.InsertEndChild(subs);
		oXml.InsertEndChild(oRoot);
		oXml.SaveFile(string(path+name+".mesh.xml").c_str());
	}

	//cout << "Export OK.\n";
	return Exit("Export OK.",0);
}
