using System;
using System.IO;
using Newtonsoft.Json;

namespace GoPro.Storage
{
	public class FileSettings<T> where T : new()
	{
		private string m_FileName;

		private T m_Data;

		public FileSettings(string filename)
		{
			m_FileName = filename;
		}

		public void Serialize()
		{
			if (m_Data != null)
			{
				string settingsFilePath = GetSettingsFilePath();
				try
				{
					File.WriteAllText(settingsFilePath, JsonConvert.SerializeObject(m_Data));
				}
				catch (Exception)
				{
				}
			}
		}

		public void Deserialize()
		{
			string settingsFilePath = GetSettingsFilePath();
			if (File.Exists(settingsFilePath))
			{
				try
				{
					m_Data = JsonConvert.DeserializeObject<T>(File.ReadAllText(settingsFilePath));
				}
				catch (Exception)
				{
				}
			}
		}

		protected T GetData()
		{
			if (m_Data == null)
			{
				Deserialize();
			}
			if (m_Data == null)
			{
				m_Data = new T();
			}
			return m_Data;
		}

		private string GetSettingsFilePath()
		{
			if (!Directory.Exists(FileHelper.UserDirectory))
			{
				Directory.CreateDirectory(FileHelper.UserDirectory);
			}
			return Path.Combine(FileHelper.UserDirectory, m_FileName);
		}
	}
}
