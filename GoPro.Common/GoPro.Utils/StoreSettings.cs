using System;
using System.IO;
using System.Net;
using System.Text;

namespace GoPro.Utils
{
	public class StoreSettings : FileSettings<StoreSettings.Data>
	{
		public class Data
		{
			public string Username;

			public string EncryptedPassword;

			public bool? IsTestingEnabled;

			public string ReelSteadyId;

			public bool? IsReelSteadyPurchased;
		}

		public const string STORE_SETTINGS_FILENAME = "StoreSettings.json";

		private string Username => GetData().Username;

		private string EncryptedPassword => GetData().EncryptedPassword;

		public bool? IsTestingEnabled
		{
			get
			{
				bool? isTestingEnabled = GetData().IsTestingEnabled;
				return (isTestingEnabled.GetValueOrDefault() && ValidateCredentials()) ? true : false;
			}
		}

		public ProductId? ReelSteadyId
		{
			get
			{
				ProductId result = ProductId.REELSTEADY;
				if (GetData().ReelSteadyId == null)
				{
					return result;
				}
				Enum.TryParse<ProductId>(GetData().ReelSteadyId, out result);
				return result;
			}
		}

		public bool? IsReelSteadyPurchased
		{
			get
			{
				bool? isReelSteadyPurchased = GetData().IsReelSteadyPurchased;
				return (isReelSteadyPurchased.GetValueOrDefault() && IsTestingEnabled.GetValueOrDefault()) ? true : false;
			}
			set
			{
				GetData().IsReelSteadyPurchased = value;
			}
		}

		private bool ValidateCredentials()
		{
			bool result = false;
			HttpWebRequest httpWebRequest = WebRequest.CreateHttp("https://artifactory-infra.gopro-platform.com/artifactory/api/security/encryptedPassword");
			string text = Convert.ToBase64String(Encoding.GetEncoding("ISO-8859-1").GetBytes($"{Username}:{EncryptedPassword}"));
			httpWebRequest.Headers.Add("Authorization", "Basic " + text);
			httpWebRequest.Method = "GET";
			try
			{
				string text2 = new StreamReader(httpWebRequest.GetResponse().GetResponseStream()).ReadToEnd();
				if (GetData().EncryptedPassword == text2)
				{
					result = true;
					return result;
				}
				return result;
			}
			catch (Exception)
			{
				return result;
			}
		}

		public StoreSettings()
			: base("StoreSettings.json")
		{
		}
	}
}
