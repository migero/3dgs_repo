using System.Collections.Generic;
using System.ComponentModel;
using System.Globalization;
using System.Resources;
using System.Threading;

namespace GoPro.Instance
{
	public class LocalizationService : INotifyPropertyChanged
	{
		private static ResourceManager m_Resources;

		private static readonly CultureInfo DEFAULT_CULTURE = CultureInfo.GetCultureInfo("en-US");

		private static readonly LocalizationService m_Instance = new LocalizationService();

		private List<CultureInfo> m_SupportedCultures;

		private CultureInfo m_Culture = DEFAULT_CULTURE;

		public static ResourceManager ResourceManager
		{
			get
			{
				return m_Resources;
			}
			set
			{
				if (m_Resources != value)
				{
					m_Resources = value;
					Instance.Culture = CultureInfo.CurrentUICulture;
				}
			}
		}

		public static LocalizationService Instance => m_Instance;

		public string this[string key]
		{
			get
			{
				string[] array = key.Split(new char[1] { '|' });
				string text = m_Resources?.GetString(array[0], m_Culture);
				if (array.Length > 1)
				{
					return string.Format(array[1], text);
				}
				return text;
			}
		}

		public List<CultureInfo> SupportedCultures
		{
			get
			{
				if (m_SupportedCultures == null)
				{
					PopulateSupportedCulturesList();
				}
				return m_SupportedCultures;
			}
		}

		public CultureInfo Culture
		{
			get
			{
				return m_Culture;
			}
			set
			{
				if (value != null && m_Culture != value)
				{
					m_Culture = GetSupportedCultureForGivenCulture(value);
					Thread.CurrentThread.CurrentUICulture = m_Culture;
					Thread.CurrentThread.CurrentCulture = m_Culture;
					this.PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(string.Empty));
				}
			}
		}

		public event PropertyChangedEventHandler PropertyChanged;

		private bool IsCultureSupported(CultureInfo culture)
		{
			if (culture == null || culture.Name == "" || ResourceManager == null)
			{
				return false;
			}
			if (GetSupportedCultureForGivenCulture(culture) != null)
			{
				return true;
			}
			return false;
		}

		private CultureInfo GetSupportedCultureForGivenCulture(CultureInfo culture)
		{
			if (culture == null || culture.Name == "" || ResourceManager == null)
			{
				return DEFAULT_CULTURE;
			}
			if (ResourceManager.GetResourceSet(culture, createIfNotExists: true, tryParents: false) != null)
			{
				return culture;
			}
			CultureInfo parent = culture.Parent;
			_ = culture.TwoLetterISOLanguageName;
			foreach (CultureInfo supportedCulture in SupportedCultures)
			{
				CultureInfo parent2 = supportedCulture.Parent;
				if (parent.Equals(parent2))
				{
					return supportedCulture;
				}
			}
			return DEFAULT_CULTURE;
		}

		private void PopulateSupportedCulturesList()
		{
			if (ResourceManager == null)
			{
				return;
			}
			m_SupportedCultures = new List<CultureInfo>();
			CultureInfo[] cultures = CultureInfo.GetCultures(CultureTypes.AllCultures);
			foreach (CultureInfo cultureInfo in cultures)
			{
				if (ResourceManager.GetResourceSet(cultureInfo, createIfNotExists: true, tryParents: false) != null)
				{
					m_SupportedCultures.Add(cultureInfo);
				}
			}
		}

		public LocalizationService()
		{
			PopulateSupportedCulturesList();
		}
	}
}
