using System;

// ReSharper disable UnusedAutoPropertyAccessor.Local

namespace mRemoteNG.App.Update
{
    public class UpdateInfo
    {
        public bool IsValid { get; private set; }
        public Version? Version { get; private set; }
        public Uri? DownloadAddress { get; private set; }
        public string? UpdateFilePath { get; set; }
        public Uri? ChangeLogAddress { get; private set; }
        public Uri? ImageAddress { get; private set; }
        public Uri? ImageLinkAddress { get; private set; }
#if !PORTABLE
        public string CertificateThumbprint { get; private set; } = string.Empty;
#endif
        // ReSharper disable once MemberCanBePrivate.Global
        public string FileName { get; set; } = string.Empty;
        public string Checksum { get; private set; } = string.Empty;

        public static UpdateInfo FromString(string input)
        {
            UpdateInfo newInfo = new();
            if (string.IsNullOrEmpty(input))
            {
                newInfo.IsValid = false;
            }
            else
            {
                UpdateFile updateFile = new(input);
                newInfo.Version = updateFile.GetVersion();
                newInfo.DownloadAddress = updateFile.GetUri("dURL");
                newInfo.ChangeLogAddress = updateFile.GetUri("clURL");
#if false
                newInfo.ImageAddress = updateFile.GetUri("imgURL");
                newInfo.ImageLinkAddress = updateFile.GetUri("imgURLLink");
#endif
#if !PORTABLE
                newInfo.CertificateThumbprint = updateFile.GetThumbprint();
#endif
                newInfo.FileName = updateFile.GetFileName();
                newInfo.Checksum = updateFile.GetChecksum();
                newInfo.IsValid = newInfo.CheckIfValid();
            }

            return newInfo;
        }

        public bool CheckIfValid()
        {
            if (string.IsNullOrEmpty(Version?.ToString()))
                return false;
            if (string.IsNullOrEmpty(DownloadAddress?.AbsoluteUri))
                return false;
            if (string.IsNullOrEmpty(ChangeLogAddress?.AbsoluteUri))
                return false;
#if false
            if (string.IsNullOrEmpty(ImageAddress.AbsoluteUri))
                return false;
            if (string.IsNullOrEmpty(ImageLinkAddress.AbsoluteUri))
                return false;
#endif
            // CertificateThumbprint is optional: an empty thumbprint means the
            // update package is unsigned and signature verification is skipped
            // (the SHA512 checksum still guarantees integrity).
            if (string.IsNullOrEmpty(FileName))
                return false;
            // ReSharper disable once ConvertIfStatementToReturnStatement
            if (string.IsNullOrEmpty(Checksum))
                return false;

            return true;
        }
    }
}