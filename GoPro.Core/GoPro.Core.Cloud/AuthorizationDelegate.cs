namespace GoPro.Core.Cloud
{
	public class AuthorizationDelegate
	{
		public RequestUserCredentials OnRequestUserCredentials;

		public RequestUserAuthorizations OnRequestUserAuthorizations;

		public RequestClientCredentials OnRequestClientCredentials;

		public UserAuthorizationsRefreshed OnUserAuthorizationsRefreshed;

		protected unsafe AuthorizationForwardingDelegate* mForwardingDelegate = null;
	}
}
