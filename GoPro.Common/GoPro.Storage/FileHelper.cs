using System;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Security.AccessControl;
using System.Security.Principal;
using GoPro.Utils;

namespace GoPro.Storage
{
	public class FileHelper
	{
		public enum FilesSelection
		{
			Last,
			Previous,
			All
		}

		public static readonly string LogFileExtension = "log";

		private static string m_ApplicationName = "";

		private static string m_UserDirectory = null;

		public static string ApplicationName
		{
			get
			{
				return m_ApplicationName;
			}
			set
			{
				m_ApplicationName = value;
			}
		}

		private static string ApplicationFileName => m_ApplicationName.Replace(' ', '.');

		public static string UserDirectory
		{
			get
			{
				if (!string.IsNullOrEmpty(m_UserDirectory))
				{
					return m_UserDirectory;
				}
				return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "GoPro", ApplicationName);
			}
			set
			{
				m_UserDirectory = value;
			}
		}

		[DllImport("shell32.dll", CharSet = CharSet.Unicode)]
		private static extern IntPtr ILCreateFromPathW(string pszPath);

		[DllImport("shell32.dll")]
		private static extern int SHOpenFolderAndSelectItems(IntPtr pidlFolder, int cild, IntPtr apidl, int dwFlags);

		[DllImport("shell32.dll")]
		private static extern void ILFree(IntPtr pidl);

		private static string GetOrCreateDirectory(string name)
		{
			string text = Path.Combine(UserDirectory, name);
			if (!Directory.Exists(text))
			{
				Directory.CreateDirectory(text);
			}
			return text;
		}

		private static string GenerateFileName(string mediaFilepath, string newExtension)
		{
			FileInfo fileInfo = new FileInfo(mediaFilepath);
			string arg = fileInfo.CreationTimeUtc.ToString("yyyy-MM-dd-HH-mm-ss");
			string arg2 = fileInfo.Length.ToString();
			return $"{arg}-{arg2}.{newExtension}";
		}

		private static string GenerateFilepath(string directory, string filename, bool unique)
		{
			string text = Path.Combine(directory, filename);
			if (unique)
			{
				uint num = 1u;
				string fileNameWithoutExtension = Path.GetFileNameWithoutExtension(filename);
				string extension = Path.GetExtension(filename);
				while (File.Exists(text))
				{
					text = Path.Combine(directory, $"{fileNameWithoutExtension} ({num}){extension}");
					num++;
				}
			}
			return text;
		}

		public static string GetAutoUpdateFilePath(string version)
		{
			return $"{UserDirectory}\\{ApplicationFileName}.{version}.msi";
		}

		public static string GetMediaTrimDirectory()
		{
			return GetOrCreateDirectory("Trims");
		}

		public static string GetMediaTrimFilePath(string mediaFilepath, bool unique)
		{
			return GenerateFilepath(GetMediaTrimDirectory(), Path.GetFileName(mediaFilepath), unique);
		}

		public static string GetExtractDirectory()
		{
			return GetOrCreateDirectory("Extracts");
		}

		public static string GetFrameExtractFilePath(string mediaFilepath, bool unique)
		{
			return GenerateFilepath(GetExtractDirectory(), Path.GetFileNameWithoutExtension(mediaFilepath) + ".jpg", unique);
		}

		public static string GetReframeDirectory()
		{
			return GetOrCreateDirectory("Reframes");
		}

		public static string GetReframeFilePath(string mediaFilepath, bool unique)
		{
			string reframeDirectory = GetReframeDirectory();
			string filename = GenerateFileName(mediaFilepath, "reframe");
			return GenerateFilepath(reframeDirectory, filename, unique);
		}

		public static string GetFeatureDirectory(string featureName)
		{
			return GetOrCreateDirectory(Path.Combine("Features", featureName));
		}

		public static string GetFeatureFilePath(string mediaFilepath, string featureName, string featureExtension, bool unique)
		{
			string featureDirectory = GetFeatureDirectory(featureName);
			string filename = GenerateFileName(mediaFilepath, featureExtension);
			return GenerateFilepath(featureDirectory, filename, unique);
		}

		public static string GetLogDirectory()
		{
			return GetOrCreateDirectory("Logs");
		}

		public static string GetLogFilePath()
		{
			string filename = string.Format("{0}.{1}", DateTime.Now.ToString("yyyy-MM-dd-HH-mm-ss"), LogFileExtension);
			return GenerateFilepath(GetLogDirectory(), filename, unique: true);
		}

		public static Exception CleanFolder(string directory, string extension, int newestFilesSkipped = 0)
		{
			try
			{
				foreach (FileInfo item in (from file in GetFileInfos(directory, extension)
					orderby file.CreationTime descending
					select file).Skip(newestFilesSkipped))
				{
					item.Delete();
				}
			}
			catch (Exception ex)
			{
				Log.Exception("Deleting old log files caused exception", ex, "C:\\a\\_temp\\WorkflowOutput\\goop-acquire-workspace\\goop\\libs\\private\\win\\lib-win-common\\src\\Storage\\FileHelper.cs", 180u, "CleanFolder");
				return ex;
			}
			return null;
		}

		public static Exception DuplicateFolderFiles(string origin, string destination, string extension, FilesSelection selection)
		{
			try
			{
				FileInfo[] fileInfos = GetFileInfos(origin, extension);
				if (fileInfos != null && fileInfos.Length != 0)
				{
					Directory.CreateDirectory(destination);
					if (Directory.Exists(destination))
					{
						switch (selection)
						{
						case FilesSelection.Last:
							if (fileInfos.Length != 0)
							{
								FileInfo fileInfo2 = fileInfos.OrderByDescending((FileInfo file) => file.CreationTime).First();
								File.Copy(fileInfo2.FullName, Path.Combine(destination, fileInfo2.Name));
							}
							break;
						case FilesSelection.Previous:
							if (fileInfos.Length > 1)
							{
								FileInfo fileInfo3 = fileInfos.OrderByDescending((FileInfo file) => file.CreationTime).Skip(1).First();
								File.Copy(fileInfo3.FullName, Path.Combine(destination, fileInfo3.Name));
							}
							break;
						case FilesSelection.All:
						{
							FileInfo[] array = fileInfos;
							foreach (FileInfo fileInfo in array)
							{
								File.Copy(fileInfo.FullName, Path.Combine(destination, fileInfo.Name));
							}
							break;
						}
						}
					}
				}
			}
			catch (Exception ex)
			{
				Log.Exception("FileHelper.DuplicateFolderFiles exception", ex, "C:\\a\\_temp\\WorkflowOutput\\goop-acquire-workspace\\goop\\libs\\private\\win\\lib-win-common\\src\\Storage\\FileHelper.cs", 233u, "DuplicateFolderFiles");
				return ex;
			}
			return null;
		}

		public static FileInfo[] GetFileInfos(string folder, string extension)
		{
			try
			{
				if (!Directory.Exists(folder))
				{
					return null;
				}
				return new DirectoryInfo(folder).GetFiles($"*.{extension}");
			}
			catch (Exception ex)
			{
				Log.Exception("FileHelper.GetFileInfos exception", ex, "C:\\a\\_temp\\WorkflowOutput\\goop-acquire-workspace\\goop\\libs\\private\\win\\lib-win-common\\src\\Storage\\FileHelper.cs", 252u, "GetFileInfos");
				return null;
			}
		}

		public static string[] GetFilePaths(string folder, string extension)
		{
			try
			{
				if (!Directory.Exists(folder))
				{
					return null;
				}
				return Directory.GetFiles(folder, extension);
			}
			catch (Exception ex)
			{
				Log.Exception("FileHelper.GetFilePaths exception", ex, "C:\\a\\_temp\\WorkflowOutput\\goop-acquire-workspace\\goop\\libs\\private\\win\\lib-win-common\\src\\Storage\\FileHelper.cs", 268u, "GetFilePaths");
				return null;
			}
		}

		public static void OpenFolderAndSelectFile(string filePath)
		{
			IntPtr intPtr = ILCreateFromPathW(filePath);
			SHOpenFolderAndSelectItems(intPtr, 0, IntPtr.Zero, 0);
			ILFree(intPtr);
		}

		public static bool FileExists(string path)
		{
			return File.Exists(path);
		}

		public static Exception FileDelete(string path)
		{
			try
			{
				File.Delete(path);
			}
			catch (Exception result)
			{
				return result;
			}
			return null;
		}

		public static Exception FileCopy(string sourceFileName, string destFileName, bool overwrite)
		{
			try
			{
				File.Copy(sourceFileName, destFileName, overwrite);
			}
			catch (Exception result)
			{
				return result;
			}
			return null;
		}

		public static Exception FileMove(string sourceFileName, string destFileName)
		{
			try
			{
				File.Move(sourceFileName, destFileName);
			}
			catch (Exception result)
			{
				return result;
			}
			return null;
		}

		public static Exception FileSetAttributes(string path, FileAttributes fileAttributes)
		{
			try
			{
				File.SetAttributes(path, fileAttributes);
			}
			catch (Exception result)
			{
				return result;
			}
			return null;
		}

		public static Exception EnsureFolderWritePermission(string filepath)
		{
			try
			{
				DirectoryInfo directoryInfo = new DirectoryInfo(Path.GetDirectoryName(filepath));
				DirectorySecurity accessControl = directoryInfo.GetAccessControl();
				FileSystemAccessRule rule = new FileSystemAccessRule(WindowsIdentity.GetCurrent().Name, FileSystemRights.Write, InheritanceFlags.ContainerInherit | InheritanceFlags.ObjectInherit, PropagationFlags.None, AccessControlType.Allow);
				accessControl.AddAccessRule(rule);
				directoryInfo.SetAccessControl(accessControl);
			}
			catch (Exception result)
			{
				return result;
			}
			return null;
		}
	}
}
